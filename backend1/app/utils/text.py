import hashlib
import re
import unicodedata

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    return WS_RE.sub(" ", TAG_RE.sub(" ", value)).strip()


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-z0-9\s]", " ", value.lower())
    return WS_RE.sub(" ", value).strip()


def slugify(value: str, max_len: int = 80) -> str:
    normalized = normalize_text(value).replace(" ", "-")
    return normalized[:max_len].strip("-") or "opportunity"


def content_hash(*parts: str | None) -> str:
    joined = "\u0001".join(normalize_text(p) for p in parts if p)
    return hashlib.sha256(joined.encode()).hexdigest()


def fingerprint(organization: str | None, title: str | None, deadline_iso: str | None) -> str:
    return hashlib.sha1(
        "|".join(
            [normalize_text(organization), normalize_text(title), (deadline_iso or "")[:10]]
        ).encode()
    ).hexdigest()


def truncate(value: str | None, limit: int = 240) -> str | None:
    if not value:
        return None
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rsplit(" ", 1)[0] + "\u2026"


def sanitize_display(value: str | None) -> str | None:
    """Remove markup/script content from text that will be rendered."""
    if not value:
        return None
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
    return strip_html(cleaned) or None
