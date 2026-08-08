from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from app.db import get_db
from app.services.matching.engine import score_opportunity
from app.utils.mongo import object_id, serialize


async def get_profile(user_id: str) -> dict:
    return await get_db().profiles.find_one({"userId": user_id}) or {"userId": user_id}


def _funded_query() -> dict:
    return {
        "$and": [
            {"fundingType": {"$ne": None}},
            {"fundingType": {"$nin": ["unpaid", "none", "unknown"]}},
        ]
    }


def build_db_query(
    *,
    q: str | None = None,
    categories: list[str] | None = None,
    remote: bool | None = None,
    funded: bool | None = None,
    deadline_before: datetime | None = None,
    deadline_after: datetime | None = None,
    countries: list[str] | None = None,
    education_levels: list[str] | None = None,
    skills: list[str] | None = None,
    include_unverified: bool = False,
) -> dict:
    clauses: list[dict] = []
    statuses = ["active", "closing_soon"]
    if include_unverified:
        statuses.append("unverified")
    clauses.append({"status": {"$in": statuses}})

    if q and q.strip():
        pattern = re.escape(q.strip()[:120])
        clauses.append(
            {
                "$or": [
                    {"title": {"$regex": pattern, "$options": "i"}},
                    {"organization": {"$regex": pattern, "$options": "i"}},
                    {"description": {"$regex": pattern, "$options": "i"}},
                    {"requiredSkills": {"$regex": pattern, "$options": "i"}},
                ]
            }
        )
    if categories:
        clauses.append({"category": {"$in": categories}})
    if remote is not None:
        clauses.append({"remote": remote})
    if funded is True:
        clauses.append(_funded_query())
    if funded is False:
        clauses.append(
            {"$or": [{"fundingType": None}, {"fundingType": {"$in": ["unpaid", "none", "unknown"]}}]}
        )
    deadline_clause = {}
    if deadline_before:
        deadline_clause["$lte"] = deadline_before
    if deadline_after:
        deadline_clause["$gte"] = deadline_after
    if deadline_clause:
        clauses.append({"deadline": deadline_clause})
    if countries:
        lowered = [re.escape(x) for x in countries if x]
        if lowered:
            clauses.append(
                {
                    "$or": [
                        {"countriesEligible": {"$regex": "|".join(lowered), "$options": "i"}},
                        {
                            "countriesEligible": {
                                "$in": ["Global", "Worldwide", "International", "All countries"]
                            }
                        },
                        {"countriesEligible": {"$size": 0}},
                        {"countriesEligible": {"$exists": False}},
                    ]
                }
            )
    if education_levels:
        clauses.append(
            {
                "$or": [
                    {"educationLevels": {"$in": education_levels}},
                    {"educationLevels": {"$size": 0}},
                    {"educationLevels": {"$exists": False}},
                ]
            }
        )
    if skills:
        skill_patterns = [re.escape(x) for x in skills if x][:12]
        if skill_patterns:
            clauses.append(
                {
                    "$or": [
                        {"requiredSkills": {"$regex": pattern, "$options": "i"}}
                        for pattern in skill_patterns
                    ]
                    + [
                        {"preferredSkills": {"$regex": pattern, "$options": "i"}}
                        for pattern in skill_patterns
                    ]
                }
            )
    return {"$and": clauses} if len(clauses) > 1 else clauses[0]


def enrich_opportunity(doc: dict, profile: dict | None = None) -> dict:
    raw = serialize(doc)
    match = score_opportunity(doc, profile or {})
    raw["match"] = match
    raw["matchScore"] = match["matchScore"]
    raw["eligibilityStatus"] = match["eligibilityStatus"]
    raw["matchedSkills"] = match["matchedSkills"]
    raw["missingSkills"] = match["missingSkills"]
    raw["matchingReasons"] = match["matchingReasons"]
    deadline = doc.get("deadline")
    if deadline:
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        raw["daysRemaining"] = max(-1, int((deadline - datetime.now(timezone.utc)).total_seconds() // 86400))
    else:
        raw["daysRemaining"] = None
    raw["applyUrl"] = raw.get("applicationUrl") or raw.get("sourceUrl")
    return raw


async def list_opportunities(
    user_id: str,
    *,
    q: str | None = None,
    categories: list[str] | None = None,
    remote: bool | None = None,
    funded: bool | None = None,
    deadline_before: datetime | None = None,
    deadline_after: datetime | None = None,
    countries: list[str] | None = None,
    education_levels: list[str] | None = None,
    skills: list[str] | None = None,
    min_match: int = 0,
    sort: str = "best_match",
    page: int = 1,
    page_size: int = 20,
    include_unverified: bool = False,
) -> dict:
    db = get_db()
    profile = await get_profile(user_id)
    query = build_db_query(
        q=q,
        categories=categories,
        remote=remote,
        funded=funded,
        deadline_before=deadline_before,
        deadline_after=deadline_after,
        countries=countries,
        education_levels=education_levels,
        skills=skills,
        include_unverified=include_unverified,
    )

    # Fetch a bounded pool because match score is user-specific and computed in Python.
    docs = await db.opportunities.find(query).sort("createdAt", -1).limit(500).to_list(500)
    items = [enrich_opportunity(doc, profile) for doc in docs]
    if min_match:
        items = [x for x in items if int(x.get("matchScore") or 0) >= min_match]

    if sort == "deadline":
        items.sort(key=lambda x: (x.get("deadline") is None, x.get("deadline") or "9999"))
    elif sort == "newest":
        items.sort(key=lambda x: x.get("createdAt") or "", reverse=True)
    else:
        items.sort(key=lambda x: int(x.get("matchScore") or 0), reverse=True)

    total = len(items)
    start = max(0, (page - 1) * page_size)
    return {
        "items": items[start : start + page_size],
        "total": total,
        "page": page,
        "pageSize": page_size,
    }


async def get_opportunity_for_user(opportunity_id: str, user_id: str) -> dict | None:
    oid = object_id(opportunity_id)
    if not oid:
        return None
    doc = await get_db().opportunities.find_one({"_id": oid})
    if not doc:
        return None
    profile = await get_profile(user_id)
    return enrich_opportunity(doc, profile)


async def dashboard_stats(user_id: str) -> dict:
    db = get_db()
    profile = await get_profile(user_id)
    docs = await db.opportunities.find(
        {"status": {"$in": ["active", "closing_soon"]}}
    ).sort("createdAt", -1).limit(500).to_list(500)
    enriched = [enrich_opportunity(x, profile) for x in docs]
    now = datetime.now(timezone.utc)
    today = now - timedelta(hours=24)
    recommended = sum(1 for x in enriched if x["matchScore"] >= 70)
    closing = sum(
        1
        for x in enriched
        if x.get("daysRemaining") is not None and 0 <= x["daysRemaining"] <= 7
    )
    new_today = 0
    for doc in docs:
        created = doc.get("createdAt")
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created and created >= today:
            new_today += 1
    saved = await db.saved_opportunities.count_documents({"userId": user_id})
    return {
        "recommended": recommended,
        "closingSoon": closing,
        "newToday": new_today,
        "saved": saved,
        "totalActive": len(enriched),
    }
