from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from app.db import get_db
from app.services.matching.engine import score_opportunity
from app.services.search_geography import applicant_eligibility, destination_matches, education_eligibility
from app.utils.mongo import object_id, serialize


# Conservative read-time hygiene for obviously non-application pages in historical data.
# Does not delete or rewrite any MongoDB record. Ingestion validation must be
# addressed separately before new records can be treated as verified.
NON_OPPORTUNITY_TITLES = re.compile(
    r"^(?:frequently asked questions|faq(?:s)?(?:\s*[-:])?|\d+\s+tips?\b|"
    r"latest (?:internship |career |student )?news\b|careers?\s*:\s*how to apply\b|"
    r".*\bcloseout\b|passion meets precision at nasa\b|"
    r"nasa virtual guest program\b)", re.IGNORECASE
)


def is_generic_content_page(doc: dict) -> bool:
    title = str(doc.get("title") or "").strip()
    return bool(NON_OPPORTUNITY_TITLES.search(title))


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
    applicant_countries: list[str] | None = None,
    destination_countries: list[str] | None = None,
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
    # Applicant-country restrictions are evaluated below using canonicalized
    # country aliases. A raw Mongo regex would miss USA/United States synonyms.
    # Student education and destination are validated after retrieval against
    # normalized values; database-only exact matching loses legitimate synonyms.

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
        applicant_countries=applicant_countries,
        destination_countries=destination_countries,
        education_levels=education_levels,
        skills=skills,
        include_unverified=include_unverified,
    )

    # Fetch a bounded pool because match score is user-specific and computed in Python.
    docs = await db.opportunities.find(query).sort("createdAt", -1).limit(500).to_list(500)
    search_profile = dict(profile)
    requested_applicants = applicant_countries or countries or []
    if len(requested_applicants) == 1:
        search_profile["country"] = requested_applicants[0]
    if len(education_levels or []) == 1:
        search_profile["educationLevel"] = education_levels[0]

    items = []
    for doc in docs:
        if is_generic_content_page(doc):
            continue
        if not destination_matches(doc.get("locations") or [], destination_countries or []):
            continue
        applicant_status = applicant_eligibility(doc.get("countriesEligible"), applicant_countries or countries or [])
        if applicant_status == "ineligible":
            continue
        education_status = education_eligibility(doc.get("educationLevels"), education_levels or [])
        if education_status == "ineligible":
            continue
        enriched = enrich_opportunity(doc, search_profile)
        enriched["searchEligibility"] = applicant_status
        enriched["searchEducationEligibility"] = education_status
        items.append(enriched)
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
    enriched = [enrich_opportunity(x, profile) for x in docs if not is_generic_content_page(x)]
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
        if is_generic_content_page(doc):
            continue
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
