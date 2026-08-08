import re
from datetime import datetime, timezone

import dateparser

DEADLINE_PATTERNS = [
    r"deadline[:\s]*(?:is\s*)?([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})",
    r"deadline[:\s]*(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})",
    r"deadline[:\s]*(\d{4}-\d{2}-\d{2})",
    r"apply(?:\s+)?(?:by|before)[:\s]*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})",
    r"closes?\s+on[:\s]*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})",
    r"applications?\s+close[sd]?[:\s]*(?:on\s*)?([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})",
    r"last date[:\s]*(?:to apply\s*)?([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})",
]

CLOSED_MARKERS = (
    "applications are closed",
    "applications closed",
    "application closed",
    "deadline has passed",
    "deadline passed",
    "no longer accepting applications",
    "this opportunity has expired",
    "submissions are closed",
)


def parse_date(value: str | None) -> datetime | None:
    """Parse a date string into a timezone-aware UTC datetime. Never guesses."""
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    if len(value) < 4 or len(value) > 120:
        return None
    dt = dateparser.parse(
        value,
        settings={
            "RETURN_AS_TIMEZONE_AWARE": True,
            "TIMEZONE": "UTC",
            "TO_TIMEZONE": "UTC",
            "PREFER_DATES_FROM": "future",
            "STRICT_PARSING": False,
        },
    )
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def extract_deadline(text: str | None) -> tuple[datetime | None, str | None]:
    """Extract a deadline from free text. Returns (datetime, original text)."""
    if not text:
        return None, None
    for pattern in DEADLINE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(1)
            parsed = parse_date(raw)
            if parsed:
                return parsed, raw
    return None, None


def has_closed_marker(text: str | None) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(marker in lowered for marker in CLOSED_MARKERS)


def days_remaining(deadline: datetime | None) -> int | None:
    if not deadline:
        return None
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    delta = deadline - datetime.now(timezone.utc)
    return int(delta.total_seconds() // 86400)
