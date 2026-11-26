"""One-off CERN SUMM-2027 migration. Preserve existing ID and backup; never create a second card."""
from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.debs import get_admin_user
from app.db import get_db
from app.models.user import User
from app.services.scrapper.extract import deterministic_extract
from app.services.scrapper.fetcher import fetch
from app.utils.urls import canonicalize_url

router = APIRouter(prefix="/admin/migrations", tags=["admin-migrations"])

SOURCE = "https://careers.cern/jobs/cern-summer-student-programme-2026-member-and-non-member-state/"
LEGACY = "https://careers.cern/programmes/summer-studentship"
EXPECTED_TITLE = "CERN Summer Student Programme 2027 (Member and Non-Member State)"
REFERENCE = "SUMM-2027"
EXPECTED_DEADLINE = datetime(2027, 1, 21, 22, 59, tzinfo=timezone.utc)
CONFIRMATION = "UPGRADE_CERN_SUMM_2027"


class MigrationRequest(BaseModel):
    execute: bool = False
    confirmation: str | None = None


def check_live_extraction(doc: dict) -> None:
    """Fail closed if page content, cycle, eligibility or apply link changes."""
    expected = {
        "title": EXPECTED_TITLE,
        "category": "internship",
        "locations": ["Geneva, Switzerland"],
        "countriesEligible": ["Worldwide"],
        "educationLevels": ["undergraduate", "masters"],
        "remote": False,
        "onsite": True,
        "fundingType": "stipend",
        "fundingAmount": 94.0,
        "currency": "CHF",
    }
    for key, value in expected.items():
        if doc.get(key) != value:
            raise HTTPException(409, f"Official source extraction mismatch: {key}")
    if doc.get("deadline") != EXPECTED_DEADLINE:
        raise HTTPException(409, "Official 2027 deadline not verified")
    url = doc.get("applicationUrl") or ""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "jobs.smartrecruiters.com" or "/company/CERN/" not in parsed.path:
        raise HTTPException(409, "Official CERN application URL not verified")
    if not doc.get("isLikelyOpportunity"):
        raise HTTPException(409, "Official page did not pass concrete opportunity gate")


async def prepare_migration(db) -> tuple[dict, dict]:
    existing = await db.opportunities.find({"title": "Summer Studentship"}).to_list(10)
    matches = [
        d for d in existing
        if canonicalize_url(d.get("sourceUrl") or "") == LEGACY
        and canonicalize_url(d.get("canonicalUrl") or LEGACY) == LEGACY
    ]
    if len(matches) != 1:
        raise HTTPException(409, f"Expected exactly one legacy overview record; matched {len(matches)}")
    old = matches[0]

    # Never overwrite if the 2027 vacancy is already present under another ID.
    collision = await db.opportunities.find_one({
        "$or": [
            {"canonicalUrl": canonicalize_url(SOURCE)},
            {"sourceUrl": SOURCE},
            {"title": EXPECTED_TITLE},
        ],
        "_id": {"$ne": old["_id"]},
    })
    if collision:
        raise HTTPException(409, "A separate SUMM-2027 record already exists; aborting duplicate risk")

    result = await fetch(SOURCE, crawl_delay=0)
    if not result.ok:
        raise HTTPException(503, "Could not fetch official CERN source for live verification")
    if urlparse(result.url).hostname != "careers.cern":
        raise HTTPException(409, "Official source redirected to an unexpected domain")
    extracted = deterministic_extract(result.url, result.html or "")
    check_live_extraction(extracted)
    # Reference is in the live source header. Never accept URL slug as cycle evidence.
    if REFERENCE not in (result.html or ""):
        raise HTTPException(409, "Official job reference missing")
    return old, extracted


@router.post("/cern-summ-2027")
async def migrate_cern_2027(payload: MigrationRequest, admin: User = Depends(get_admin_user)):
    if payload.execute and payload.confirmation != CONFIRMATION:
        raise HTTPException(400, "Explicit confirmation required for a write")

    db = get_db()
    old, extracted = await prepare_migration(db)
    now = datetime.now(timezone.utc)

    proposed = {
        "title": EXPECTED_TITLE,
        "organization": "CERN",
        "category": "internship",
        "sourceUrl": SOURCE,
        "canonicalUrl": canonicalize_url(SOURCE),
        "sourceDomain": "careers.cern",
        "applicationUrl": extracted["applicationUrl"],
        "description": extracted.get("description"),
        "shortDescription": extracted.get("shortDescription"),
        "deadline": EXPECTED_DEADLINE,
        "deadlineText": extracted.get("deadlineText"),
        "locations": ["Geneva, Switzerland"],
        "countriesEligible": ["Worldwide"],
        "educationLevels": ["undergraduate", "masters"],
        "fieldsOfStudy": extracted.get("fieldsOfStudy") or [],
        "requiredSkills": extracted.get("requiredSkills") or [],
        "remote": False, "hybrid": False, "onsite": True,
        "fundingType": "stipend",
        "fundingAmount": 94.0, "currency": "CHF",
        "requirements": extracted.get("requirements") or [],
        "benefits": extracted.get("benefits") or [],
        "eligibilityText": extracted.get("eligibilityText"),
        "verified": True, "verificationStatus": "verified",
        "status": "active",
        "extractionMethod": "official-live-html-manual-migration",
        "lastCheckedAt": now, "lastSeenAt": now,
        "lastChangedAt": now, "updatedAt": now,
    }
    summary = {
        "recordId": str(old["_id"]),
        "previousTitle": old.get("title"),
        "newTitle": EXPECTED_TITLE,
        "deadline": EXPECTED_DEADLINE.isoformat(),
        "sourceUrl": SOURCE,
        "applicationUrl": extracted["applicationUrl"],
        "category": "internship",
        "location": "Geneva, Switzerland",
        "applicantEligibility": "Worldwide",
        "educationLevels": proposed["educationLevels"],
    }
    if not payload.execute:
        return {"status": "dry_run", "wrote": False, **summary}

    # Snapshot must exist before any mutation; never overwrite this backup.
    backup_id = f"cern-summ-2027:{old['_id']}"
    previous_backup = await db.opportunity_migration_backups.find_one({"_id": backup_id})
    if previous_backup:
        raise HTTPException(409, "Migration backup already exists; stop and review state")
    await db.opportunity_migration_backups.insert_one({
        "_id": backup_id, "migration": "cern-summ-2027",
        "recordId": old["_id"], "capturedAt": now,
        "performedBy": admin.id, "original": old,
    })

    # Compare-and-swap: do not overwrite a record changed since dry-run.
    result = await db.opportunities.update_one({
        "_id": old["_id"],
        "title": "Summer Studentship",
        "sourceUrl": old["sourceUrl"],
        "canonicalUrl": old["canonicalUrl"],
        "updatedAt": old.get("updatedAt"),
    }, {"$set": proposed})
    if result.matched_count != 1 or result.modified_count != 1:
        raise HTTPException(409, "Concurrent update detected; source record untouched, backup retained")

    updated = await db.opportunities.find_one({"_id": old["_id"]})
    if not updated or updated.get("title") != EXPECTED_TITLE or updated.get("deadline") != EXPECTED_DEADLINE:
        raise HTTPException(500, "Post-write read-back mismatch; inspect migration backup")
    return {"status": "updated", "wrote": True, "backupId": backup_id, **summary}
