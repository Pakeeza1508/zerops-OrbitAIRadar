
"""Deterministic matching engine — no LLM calls per user/opportunity pair.

Weights (total 100):
  skills 28 | eligibility/country 25 | category preference 14
  education 10 | location/remote 8 | experience 5 | deadline usefulness 5 | funding 5
Unknown data is treated as neutral (partial credit), never as a failure.
"""

from app.utils.dates import days_remaining
from app.utils.text import normalize_text

WEIGHTS = {
    "skills": 28.0,
    "eligibility": 25.0,
    "category": 14.0,
    "education": 10.0,
    "location": 8.0,
    "experience": 5.0,
    "deadline": 5.0,
    "funding": 5.0,
}

GLOBAL_MARKERS = {"global", "worldwide", "any country", "international", "all countries", "open"}

EXPERIENCE_ORDER = ["student", "beginner", "entry", "junior", "mid", "senior"]


def _norm_set(values) -> set[str]:
    return {normalize_text(v) for v in (values or []) if v and normalize_text(v)}


def _skill_score(profile_skills: set[str], required: set[str], preferred: set[str]):
    target = required | preferred
    if not target:
        return 0.6, [], []
    matched = sorted(target & profile_skills)
    missing = sorted(required - profile_skills)
    if not profile_skills:
        return 0.4, matched, missing
    required_ratio = len(required & profile_skills) / len(required) if required else None
    overall_ratio = len(matched) / len(target)
    ratio = overall_ratio if required_ratio is None else (0.7 * required_ratio + 0.3 * overall_ratio)
    return min(1.0, 0.15 + 0.85 * ratio), matched, missing


def _eligibility(country: str | None, eligible: list[str]):
    normalized = _norm_set(eligible)
    if not normalized:
        return 0.6, "uncertain", "Eligible countries are not stated on the source page"
    if normalized & GLOBAL_MARKERS:
        return 1.0, "eligible", "Open to applicants worldwide"
    if not country:
        return 0.5, "uncertain", "Add your country to your profile for eligibility checks"
    c = normalize_text(country)
    for item in normalized:
        if c == item or c in item or item in c:
            return 1.0, "eligible", f"Applicants from {country} are accepted"
    return 0.15, "likely_ineligible", f"{country} is not listed among eligible countries"


def _category(preferred: list[str], category: str | None):
    if not preferred:
        return 0.7, None
    if category and category in {p.strip().lower() for p in preferred}:
        return 1.0, f"Matches your interest in {category.replace('_', ' ')} opportunities"
    return 0.3, None


def _education(level: str | None, levels: list[str]):
    normalized = _norm_set(levels)
    if not normalized:
        return 0.65, None
    if not level:
        return 0.5, None
    n = normalize_text(level)
    for item in normalized:
        if n == item or n in item or item in n:
            return 1.0, f"Open to {level} students"
    return 0.35, None


def _location(prefs: list[str], opp: dict):
    prefs_n = {normalize_text(p) for p in (prefs or [])}
    if not prefs_n:
        return 0.7, None
    if "global" in prefs_n:
        return 1.0, None
    if opp.get("remote") and "remote" in prefs_n:
        return 1.0, "Fully remote, matching your preference"
    if opp.get("hybrid") and "hybrid" in prefs_n:
        return 0.9, "Hybrid participation available"
    if opp.get("onsite") and "onsite" in prefs_n:
        return 0.85, None
    if opp.get("remote") is None and opp.get("hybrid") is None and opp.get("onsite") is None:
        return 0.6, None
    return 0.35, None


def _experience(level: str | None, levels: list[str]):
    normalized = _norm_set(levels)
    if not normalized or not level:
        return 0.65, None
    n = normalize_text(level)
    if any(n == item or n in item or item in n for item in normalized):
        return 1.0, f"Suited to {level} experience level"
    return 0.4, None


def _deadline(deadline):
    days = days_remaining(deadline)
    if days is None:
        return 0.5, None
    if days < 0:
        return 0.0, "Deadline has passed"
    if days <= 7:
        return 1.0, f"Closing in {days} day(s) — apply soon"
    if days <= 45:
        return 0.9, f"{days} days left to apply"
    if days <= 180:
        return 0.7, f"{days} days left to apply"
    return 0.5, None



def _funding(preference: str | None, funding_type: str | None):
    pref = normalize_text(preference)
    funding = normalize_text(funding_type)
    if not pref or pref in {"any", "unfunded ok", "unfunded_ok"}:
        return 0.7, None
    if pref in {"funded only", "funded_only", "fully funded", "funded"}:
        if not funding:
            return 0.5, "Funding is not clearly stated"
        if funding in {"unpaid", "none", "unfunded"}:
            return 0.0, "This appears to be unfunded"
        return 1.0, f"Funding preference matched: {funding_type}"
    return 0.7, None


def _display_skill(value: str) -> str:
    special = {
        "ai": "AI", "nlp": "NLP", "sql": "SQL", "aws": "AWS",
        "ui ux": "UI/UX", "c++": "C++", "c#": "C#", "node js": "Node.js",
        "javascript": "JavaScript", "typescript": "TypeScript",
    }
    return special.get(value, value.title())


def score_opportunity(opportunity: dict, profile: dict | None) -> dict:
    profile = profile or {}
    profile_skills = _norm_set(profile.get("skills")) | _norm_set(profile.get("interests"))

    skill_s, matched, missing = _skill_score(
        profile_skills,
        _norm_set(opportunity.get("requiredSkills")),
        _norm_set(opportunity.get("preferredSkills")),
    )
    elig_s, elig_status, elig_reason = _eligibility(
        profile.get("country"), opportunity.get("countriesEligible") or []
    )
    cat_s, cat_reason = _category(
        profile.get("preferredCategories") or [], opportunity.get("category")
    )
    edu_s, edu_reason = _education(
        profile.get("educationLevel"), opportunity.get("educationLevels") or []
    )
    loc_s, loc_reason = _location(profile.get("locationPreference") or [], opportunity)
    exp_s, exp_reason = _experience(
        profile.get("experienceLevel"), opportunity.get("experienceLevels") or []
    )
    dl_s, dl_reason = _deadline(opportunity.get("deadline"))
    fund_s, fund_reason = _funding(profile.get("fundingPreference"), opportunity.get("fundingType"))

    breakdown = {
        "skills": round(skill_s * WEIGHTS["skills"], 1),
        "eligibility": round(elig_s * WEIGHTS["eligibility"], 1),
        "category": round(cat_s * WEIGHTS["category"], 1),
        "education": round(edu_s * WEIGHTS["education"], 1),
        "location": round(loc_s * WEIGHTS["location"], 1),
        "experience": round(exp_s * WEIGHTS["experience"], 1),
        "deadline": round(dl_s * WEIGHTS["deadline"], 1),
        "funding": round(fund_s * WEIGHTS["funding"], 1),
    }
    total = int(round(sum(breakdown.values())))

    if elig_status == "eligible" and total >= 70:
        eligibility_status = "eligible"
    elif elig_status == "likely_ineligible":
        eligibility_status = "likely_ineligible"
    elif elig_status == "eligible":
        eligibility_status = "likely_eligible"
    else:
        eligibility_status = "uncertain"

    reasons = []
    if matched:
        reasons.append("Skill overlap: " + ", ".join(sorted(matched)[:4]))
    for reason in (elig_reason, cat_reason, edu_reason, loc_reason, exp_reason, dl_reason, fund_reason):
        if reason:
            reasons.append(reason)
    if opportunity.get("fundingType") and not fund_reason:
        reasons.append(f"Funding: {opportunity['fundingType']}")

    return {
        "matchScore": max(0, min(100, total)),
        "eligibilityStatus": eligibility_status,
        "matchedSkills": [_display_skill(s) for s in matched][:12],
        "missingSkills": [_display_skill(s) for s in missing][:12],
        "matchingReasons": reasons[:6],
        "breakdown": breakdown,
    }

