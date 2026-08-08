from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.config import settings
from app.db import get_db
from app.models.run import ScrapeRun
from app.services.ai.groq_client import groq_client
from app.services.ai.tasks import classify_page, extract_opportunity
from app.services.scrapper.dedupe import find_existing, is_duplicate_of
from app.services.scrapper.discovery import discover_query, discover_source
from app.services.scrapper.extract import deterministic_extract
from app.services.scrapper.fetcher import fetch, fetch_rendered
from app.services.scrapper.normalize import build_opportunity
from app.utils.mongo import serialize
from app.utils.urls import canonicalize_url

logger = logging.getLogger("orbit.ingestion")


async def _acquire_lock(name: str = "opportunity-sync", ttl_minutes: int = 45) -> bool:
    """Atomically claim the singleton ingestion lock.

    The unique `name` index makes concurrent upserts safe: if another worker already
    owns an unexpired lock, its insert attempt collides and we return False.
    """
    db = get_db()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=ttl_minutes)
    try:
        result = await db.locks.update_one(
            {
                "name": name,
                "$or": [
                    {"expiresAt": {"$lte": now}},
                    {"expiresAt": {"$exists": False}},
                ],
            },
            {"$set": {"name": name, "acquiredAt": now, "expiresAt": expires}},
            upsert=True,
        )
        return bool(result.matched_count or result.upserted_id)
    except DuplicateKeyError:
        return False


async def _release_lock(name: str = "opportunity-sync") -> None:
    await get_db().locks.delete_one({"name": name})


async def create_run(trigger: str = "manual") -> str:
    run = ScrapeRun(trigger=trigger)
    doc = run.to_mongo(exclude_none=True)
    result = await get_db().scrape_runs.insert_one(doc)
    return str(result.inserted_id)


async def get_run(run_id: str) -> dict | None:
    try:
        oid = ObjectId(run_id)
    except Exception:
        return None
    return await get_db().scrape_runs.find_one({"_id": oid})


async def _finish_run(run_id: str, metrics: dict, status: str, errors: list[str]) -> None:
    try:
        oid = ObjectId(run_id)
    except Exception:
        return
    await get_db().scrape_runs.update_one(
        {"_id": oid},
        {
            "$set": {
                **metrics,
                "status": status,
                "errors": errors[-25:],
                "finishedAt": datetime.now(timezone.utc),
            }
        },
    )


async def _mark_fetch_failure(existing: dict | None, gone: bool) -> None:
    if not existing:
        return
    db = get_db()
    failures = int(existing.get("consecutiveFetchFailures") or 0) + 1
    update = {
        "consecutiveFetchFailures": failures,
        "lastCheckedAt": datetime.now(timezone.utc),
    }
    if gone and failures >= settings.consecutive_gone_threshold:
        update["status"] = "closed"
    await db.opportunities.update_one({"_id": existing["_id"]}, {"$set": update})


async def expire_old_opportunities() -> int:
    """Remove dead master records while preserving independent saved snapshots."""
    db = get_db()
    now = datetime.now(timezone.utc)

    # Normalize statuses first.
    result = await db.opportunities.update_many(
        {
            "deadline": {"$lt": now},
            "status": {"$in": ["active", "closing_soon", "unverified"]},
        },
        {"$set": {"status": "expired", "updatedAt": now}},
    )
    expired_count = int(result.modified_count)

    if not settings.delete_expired_master:
        return expired_count

    cursor = db.opportunities.find(
        {"status": {"$in": ["expired", "closed"]}},
        {"_id": 1},
    )
    ids_to_delete = []
    async for doc in cursor:
        opp_id = str(doc["_id"])
        await db.saved_opportunities.update_many(
            {"originalOpportunityId": opp_id},
            {"$set": {"masterDeleted": True, "updatedAt": now}},
        )
        ids_to_delete.append(doc["_id"])

    if ids_to_delete:
        await db.opportunities.delete_many({"_id": {"$in": ids_to_delete}})
    return expired_count


async def ingest_candidate(
    candidate: dict,
    source: dict | None,
    ai_budget_remaining: int,
) -> dict:
    db = get_db()
    url = canonicalize_url(candidate.get("url", ""))
    if not url:
        return {"state": "failed", "aiCalls": 0, "error": "invalid candidate URL"}

    existing = await db.opportunities.find_one({"canonicalUrl": url})
    result = await fetch(
        url,
        crawl_delay=float((source or {}).get("crawlDelay") or settings.scraper_default_delay),
    )
    if not result.ok:
        await _mark_fetch_failure(existing, result.gone)
        return {
            "state": "failed",
            "aiCalls": 0,
            "error": result.error or f"fetch failed ({result.status})",
        }

    deterministic = deterministic_extract(
        result.url,
        result.html or "",
        category_hint=(source or {}).get("category"),
    )

    # JS shell / very weak parse: optional rendered fallback.
    if deterministic.get("completeness", 0) < 0.25 and len(deterministic.get("text") or "") < 500:
        rendered = await fetch_rendered(result.url)
        if rendered.ok and rendered.html:
            deterministic = deterministic_extract(
                rendered.url,
                rendered.html,
                category_hint=(source or {}).get("category"),
            )

    # Cheap unchanged check before any AI call.
    preliminary = build_opportunity(
        result.url,
        deterministic,
        None,
        str((source or {}).get("_id")) if (source or {}).get("_id") else None,
        candidate.get("sourceType") or (source or {}).get("discoveryType") or "listing",
    )
    if preliminary and existing and existing.get("contentHash") == preliminary.contentHash:
        await db.opportunities.update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "lastSeenAt": datetime.now(timezone.utc),
                    "lastCheckedAt": datetime.now(timezone.utc),
                    "consecutiveFetchFailures": 0,
                }
            },
        )
        return {"state": "unchanged", "aiCalls": 0}

    ai_data = None
    ai_calls = 0
    ambiguous_page = not bool(deterministic.get("isLikelyOpportunity"))

    # Precision gate: generic listing/index pages should not become opportunity cards.
    # If Groq is configured, ambiguous pages get one cheap classifier call. Without
    # Groq we accept only deterministic pages with strong concrete-opportunity signals.
    if ambiguous_page:
        if not groq_client.enabled or ai_budget_remaining <= 0:
            return {"state": "rejected", "aiCalls": 0}
        before = groq_client.calls_made
        classification = await classify_page(
            deterministic.get("title") or candidate.get("title") or "",
            deterministic.get("text") or "",
        )
        ai_calls += max(0, groq_client.calls_made - before)
        if not isinstance(classification, dict) or not classification.get("isOpportunity"):
            return {"state": "rejected", "aiCalls": ai_calls}

    needs_extraction_ai = (
        groq_client.enabled
        and ai_budget_remaining > ai_calls
        and deterministic.get("completeness", 0) < settings.min_ai_extraction_completeness
    )
    if needs_extraction_ai:
        before = groq_client.calls_made
        ai_data = await extract_opportunity(
            result.url,
            deterministic.get("title") or candidate.get("title") or "",
            deterministic.get("text") or "",
        )
        ai_calls += max(0, groq_client.calls_made - before)
        if isinstance(ai_data, dict) and ai_data.get("isOpportunity") is False:
            return {"state": "rejected", "aiCalls": ai_calls}

    opportunity = build_opportunity(
        result.url,
        deterministic,
        ai_data,
        str((source or {}).get("_id")) if (source or {}).get("_id") else None,
        candidate.get("sourceType") or (source or {}).get("discoveryType") or "listing",
    )
    if not opportunity:
        return {"state": "rejected", "aiCalls": ai_calls}

    found = await find_existing(db, opportunity)
    now = datetime.now(timezone.utc)
    if found:
        if is_duplicate_of(found, opportunity):
            await db.opportunities.update_one(
                {"_id": found["_id"]},
                {"$set": {"lastSeenAt": now, "lastCheckedAt": now}},
            )
            return {"state": "duplicate", "aiCalls": ai_calls}

        new_doc = opportunity.to_mongo(exclude_none=True)
        new_doc.pop("_id", None)
        new_doc["createdAt"] = found.get("createdAt", new_doc.get("createdAt", now))
        new_doc["lastChangedAt"] = now
        new_doc["consecutiveFetchFailures"] = 0
        await db.opportunities.update_one({"_id": found["_id"]}, {"$set": new_doc})
        return {"state": "updated", "aiCalls": ai_calls, "id": str(found["_id"])}

    doc = opportunity.to_mongo(exclude_none=True)
    doc["consecutiveFetchFailures"] = 0
    inserted = await db.opportunities.insert_one(doc)
    return {"state": "new", "aiCalls": ai_calls, "id": str(inserted.inserted_id)}


async def run_ingestion(
    trigger: str = "manual",
    query: str | None = None,
    max_candidates: int | None = None,
    run_id: str | None = None,
) -> dict:
    db = get_db()
    run_id = run_id or await create_run(trigger)
    max_candidates = min(
        max_candidates or settings.max_candidates_per_run,
        200,
    )

    metrics = {
        "sourcesAttempted": 0,
        "sourcesSucceeded": 0,
        "urlsDiscovered": 0,
        "urlsFetched": 0,
        "newCount": 0,
        "updatedCount": 0,
        "duplicateCount": 0,
        "expiredCount": 0,
        "failedCount": 0,
        "aiCalls": 0,
    }
    errors: list[str] = []

    if not await _acquire_lock():
        errors.append("Another ingestion run is already active")
        await _finish_run(run_id, metrics, "failed", errors)
        doc = await get_run(run_id)
        return serialize(doc or {"id": run_id, **metrics, "status": "failed", "errors": errors})

    try:
        candidates: list[tuple[dict, dict | None]] = []

        if query and query.strip():
            discovered = await discover_query(query.strip(), max_results=max_candidates)
            candidates.extend((item, None) for item in discovered)

        # Registry crawling remains the primary discovery path, even when SearXNG is absent.
        if len(candidates) < max_candidates:
            sources = await db.sources.find({"enabled": True}).sort("priority", -1).to_list(100)
            for source in sources:
                if len(candidates) >= max_candidates:
                    break
                metrics["sourcesAttempted"] += 1
                now = datetime.now(timezone.utc)
                await db.sources.update_one({"_id": source["_id"]}, {"$set": {"lastRunAt": now}})
                try:
                    items = await discover_source(
                        source,
                        max_results=min(
                            settings.max_urls_per_source,
                            max_candidates - len(candidates),
                        ),
                    )
                    metrics["sourcesSucceeded"] += 1
                    await db.sources.update_one(
                        {"_id": source["_id"]},
                        {
                            "$set": {
                                "lastSuccessAt": now,
                                "lastError": None,
                                "consecutiveFailures": 0,
                            }
                        },
                    )
                    candidates.extend((item, source) for item in items)
                except Exception as exc:
                    message = f"{source.get('name', 'source')}: {str(exc)[:180]}"
                    errors.append(message)
                    await db.sources.update_one(
                        {"_id": source["_id"]},
                        {
                            "$set": {"lastError": str(exc)[:400]},
                            "$inc": {"consecutiveFailures": 1},
                        },
                    )

        # Canonical URL dedupe before fetching.
        unique: list[tuple[dict, dict | None]] = []
        seen = set()
        for candidate, source in candidates:
            url = canonicalize_url(candidate.get("url", ""))
            if not url or url in seen:
                continue
            seen.add(url)
            candidate = {**candidate, "url": url}
            unique.append((candidate, source))
            if len(unique) >= max_candidates:
                break

        metrics["urlsDiscovered"] = len(unique)

        for candidate, source in unique:
            ai_remaining = max(0, settings.max_ai_calls_per_sync - metrics["aiCalls"])
            outcome = await ingest_candidate(candidate, source, ai_remaining)
            state = outcome.get("state")
            metrics["aiCalls"] += int(outcome.get("aiCalls") or 0)
            if state not in {"failed"}:
                metrics["urlsFetched"] += 1
            if state == "new":
                metrics["newCount"] += 1
            elif state == "updated":
                metrics["updatedCount"] += 1
            elif state == "duplicate":
                metrics["duplicateCount"] += 1
            elif state == "failed":
                metrics["failedCount"] += 1
                if outcome.get("error"):
                    errors.append(f"{candidate.get('url')}: {outcome['error'][:180]}")

        metrics["expiredCount"] = await expire_old_opportunities()
        if metrics["failedCount"] and (metrics["newCount"] or metrics["updatedCount"] or metrics["urlsFetched"]):
            status = "partial"
        elif metrics["failedCount"] and not metrics["urlsFetched"]:
            status = "failed"
        else:
            status = "success"

        await _finish_run(run_id, metrics, status, errors)
    except Exception as exc:
        logger.exception("Ingestion run failed")
        errors.append(str(exc)[:500])
        await _finish_run(run_id, metrics, "failed", errors)
    finally:
        await _release_lock()

    doc = await get_run(run_id)
    return serialize(doc or {"id": run_id, **metrics, "status": "failed", "errors": errors})
