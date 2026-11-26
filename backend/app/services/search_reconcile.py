"""Pure search-filter reconciliation: deterministic explicit intent overrides model guesses."""
from __future__ import annotations

from app.services.search import deterministic_query_filters
from app.services.search_geography import geography_from_query, normalize_country

LIST_FIELDS = ("categories", "skills", "educationLevels")
BOOLEAN_DATE_FIELDS = ("remote", "fundingRequired", "deadlineBefore", "deadlineAfter")


def reconcile_ai_filters(query: str, ai_response: object) -> tuple[dict, bool, str]:
    """Return (filters, used_ai, source_reason); never trust unsanitized LLM filters."""
    fallback = deterministic_query_filters(query)
    if not isinstance(ai_response, dict):
        return fallback, False, "ai_unavailable_or_invalid"

    # Missing schema keys or wrong data types indicate an incomplete JSON response.
    required = {"categories", "skills", "remote", "fundingRequired",
                "educationLevels", "applicantCountries", "destinationCountries"}
    if not required.issubset(ai_response):
        return fallback, False, "ai_incomplete"
    if any(not isinstance(ai_response[key], list) for key in LIST_FIELDS + (
        "applicantCountries", "destinationCountries"
    )):
        return fallback, False, "ai_invalid_schema"

    raw = dict(ai_response)
    for key in LIST_FIELDS:
        explicit = fallback.get(key) or []
        if explicit:
            raw[key] = explicit
    for key in BOOLEAN_DATE_FIELDS:
        if fallback.get(key) is not None:
            raw[key] = fallback[key]

    if any(fallback.get(key) for key in (
        "categories", "skills", "educationLevels", "applicantCountries",
        "destinationCountries", "remote", "fundingRequired", "deadlineBefore",
    )):
        raw["queryText"] = None

    explicit_geo = geography_from_query(query)
    raw["applicantCountries"] = explicit_geo["applicantCountries"] or [
        normalize_country(item) for item in raw.get("applicantCountries", [])
        if isinstance(item, str) and item.strip()
    ]
    raw["destinationCountries"] = explicit_geo["destinationCountries"] or [
        normalize_country(item) for item in raw.get("destinationCountries", [])
        if isinstance(item, str) and item.strip()
    ]
    if not explicit_geo["destinationCountries"]:
        raw["destinationCountries"] = [
            item for item in raw["destinationCountries"]
            if item not in raw["applicantCountries"]
        ]
    if any(marker in query.lower() for marker in (
        "worldwide", "globally", "anywhere in the world", "across the world"
    )):
        raw["destinationCountries"] = []

    raw["countries"] = []
    return raw, True, "ai_validated"
