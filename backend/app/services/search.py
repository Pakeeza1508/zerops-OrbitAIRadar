from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from app.models.opportunity import CATEGORIES
from app.services.scrapper.extract import SKILL_VOCAB
from app.services.search_geography import geography_from_query


def deterministic_query_filters(query: str) -> dict:
    text = (query or "").strip()
    lowered = text.lower()
    categories = []
    aliases = {
        "scholarship": ("scholarship", "scholarships", "bursary"),
        "internship": ("internship", "internships", "intern"),
        "fellowship": ("fellowship", "fellowships"),
        "hackathon": ("hackathon", "hackathons"),
        "grant": ("grant", "grants"),
        "competition": ("competition", "competitions", "contest", "challenge"),
        "research": ("research", "research program", "research programme"),
        "open_source": ("open source", "gsoc", "outreachy"),
        "developer_program": ("developer program", "developer programme", "ambassador"),
        "mentorship": ("mentorship", "mentor program", "mentoring"),
    }
    for category, terms in aliases.items():
        if any(term in lowered for term in terms):
            categories.append(category)

    skills = []
    for skill in SKILL_VOCAB:
        if re.search(r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])", lowered):
            skills.append(skill)

    remote = True if "remote" in lowered or "work from home" in lowered else None
    funding_required = True if any(
        term in lowered
        for term in ("fully funded", "funded", "stipend", "paid", "scholarship")
    ) else None

    geography = geography_from_query(text)

    education_levels = []
    if re.search(r"\b(?:undergraduate|undergrads?|bachelors?|b\.?sc)\b", lowered):
        education_levels.append("undergraduate")
    if re.search(r"\b(?:masters?|postgraduate|m\.?sc)\b", lowered):
        education_levels.append("masters")
    if re.search(r"\b(?:phd|doctoral|doctorate)\b", lowered):
        education_levels.append("phd")

    deadline_before = None
    deadline_after = None
    now = datetime.now(timezone.utc)
    m = re.search(r"(?:next|within)\s+(\d{1,3})\s+days", lowered)
    if m:
        deadline_after = now
        deadline_before = now + timedelta(days=min(int(m.group(1)), 365))
    elif re.search(r"\b(?:closing|deadline|ends?)\s+(?:by\s+)?tomorrow\b", lowered):
        tomorrow = (now + timedelta(days=1)).date()
        deadline_after = now
        deadline_before = datetime.combine(tomorrow, datetime.max.time(), tzinfo=timezone.utc)

    return {
        "categories": categories,
        "countries": [],
        **geography,
        "skills": skills,
        "remote": remote,
        "fundingRequired": funding_required,
        "deadlineBefore": deadline_before,
        "deadlineAfter": deadline_after,
        "educationLevels": education_levels,
        "queryText": text if not categories and not skills else None,
        "answer": f"Filtered opportunities using the available profile and query terms: {text}",
    }
