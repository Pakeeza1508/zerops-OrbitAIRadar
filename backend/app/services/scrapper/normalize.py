"""Merge deterministic + AI extraction into a validated Opportunity document."""

from datetime import datetime, timezone

from app.models.opportunity import CATEGORIES, Opportunity
from app.utils.dates import days_remaining, parse_date
from app.utils.text import content_hash, fingerprint, sanitize_display, slugify, truncate
from app.utils.urls import canonicalize_url, domain_of

MIN_TITLE_LEN = 10


def _clean_list(values, limit: int = 20) -> list[str]:
    out, seen = [], set()
    for value in values or []:
        if not isinstance(value, str):
            continue
        value = sanitize_display(value)
        if not value or len(value) > 300:
            continue
        key = value.lower()
        if key not in seen:
            seen.add(key)
            out.append(value)
        if len(out) >= limit:
            break
    return out


def compute_status(deadline: datetime | None, closed: bool, verification: str) -> str:
    if closed:
        return "closed"
    days = days_remaining(deadline)
    if days is not None and days < 0:
        return "expired"
    if verification == "unverified":
        return "unverified"
    if days is not None and days <= 7:
        return "closing_soon"
    return "active"


def build_opportunity(
    url: str,
    deterministic: dict,
    ai: dict | None,
    source_id: str | None,
    source_type: str,
) -> Opportunity | None:
    """Combine extraction outputs. AI never overrides deterministic facts."""
    ai = ai or {}

    title = deterministic.get("title") or ai.get("title")
    if not title or len(title.strip()) < MIN_TITLE_LEN:
        return None

    canonical_raw = deterministic.get("canonical") or url
    canonical = canonicalize_url(canonical_raw) or canonicalize_url(url)
    if not canonical:
        return None

    description = sanitize_display(deterministic.get("description") or ai.get("description"))
    category = deterministic.get("category") or ai.get("category") or "other"
    if category not in CATEGORIES:
        category = "other"

    deadline = deterministic.get("deadline")
    deadline_text = deterministic.get("deadlineText")
    if not deadline and ai.get("deadline"):
        deadline = parse_date(str(ai["deadline"]))
        deadline_text = str(ai["deadline"]) if deadline else None

    countries = _clean_list(deterministic.get("countriesEligible") or ai.get("countriesEligible"))
    education = _clean_list(deterministic.get("educationLevels") or ai.get("educationLevels"), 10)
    fields = _clean_list(deterministic.get("fieldsOfStudy") or ai.get("fieldsOfStudy"), 10)
    skills = _clean_list(deterministic.get("requiredSkills") or ai.get("requiredSkills"), 20)
    requirements = _clean_list(deterministic.get("requirements") or ai.get("requirements"))
    benefits = _clean_list(deterministic.get("benefits") or ai.get("benefits"))

    funding_type = deterministic.get("fundingType") or ai.get("fundingType")
    funding_amount = deterministic.get("fundingAmount")
    if funding_amount is None and isinstance(ai.get("fundingAmount"), (int, float)):
        funding_amount = float(ai["fundingAmount"])
    currency = deterministic.get("currency") or ai.get("currency")

    remote = deterministic.get("remote")
    if remote is None and isinstance(ai.get("remote"), bool):
        remote = ai["remote"]

    ai_confidence = ai.get("confidence") if isinstance(ai.get("confidence"), (int, float)) else None
    completeness = deterministic.get("completeness", 0)

    is_primary = source_type in ("rss", "sitemap", "listing", "manual", "seed")
    if is_primary and (deterministic.get("usedJsonLd") or completeness >= 0.5):
        verification = "verified"
    elif completeness >= 0.375 or (ai_confidence or 0) >= 0.7:
        verification = "likely_verified"
    else:
        verification = "unverified"

    now = datetime.now(timezone.utc)
    text_for_hash = (deterministic.get("text") or "")[:20000]
    chash = content_hash(title, description, text_for_hash)

    application_url = ai.get("applicationUrl") if isinstance(ai.get("applicationUrl"), str) else None
    if application_url:
        application_url = canonicalize_url(application_url) or None

    organization = sanitize_display(deterministic.get("organization") or ai.get("organization"))
    if organization:
        organization = organization[:140]

    return Opportunity(
        title=sanitize_display(title)[:220],
        organization=organization or domain_of(canonical),
        slug=slugify(title),
        description=truncate(description, 4000),
        shortDescription=truncate(description, 200),
        category=category,
        sourceUrl=url,
        applicationUrl=application_url,
        canonicalUrl=canonical,
        sourceDomain=domain_of(canonical),
        countriesEligible=countries,
        locations=_clean_list(deterministic.get("locations"), 8),
        remote=remote,
        hybrid=deterministic.get("hybrid"),
        onsite=deterministic.get("onsite"),
        educationLevels=education,
        fieldsOfStudy=fields,
        requiredSkills=skills,
        preferredSkills=[],
        experienceLevels=[],
        fundingType=funding_type,
        fundingAmount=funding_amount,
        currency=currency,
        deadline=deadline,
        deadlineText=truncate(deadline_text, 120),
        applicationOpenDate=deterministic.get("applicationOpenDate"),
        eligibilityText=truncate(deterministic.get("eligibilityText"), 900),
        requirements=requirements,
        benefits=benefits,
        verified=verification == "verified",
        verificationStatus=verification,
        sourceType=source_type,
        extractionMethod="jsonld+html" + ("+ai" if ai else ""),
        aiConfidence=float(ai_confidence) if ai_confidence is not None else None,
        status=compute_status(deadline, bool(deterministic.get("closedMarker")), verification),
        scrapedAt=now,
        lastSeenAt=now,
        lastCheckedAt=now,
        lastChangedAt=now,
        contentHash=chash,
        fingerprint=fingerprint(
            organization or domain_of(canonical), title, deadline.isoformat() if deadline else None
        ),
        sourceId=source_id,
        createdAt=now,
        updatedAt=now,
    )
