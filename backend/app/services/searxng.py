"""Optional SearXNG discovery. Disabled silently when SEARXNG_BASE_URL is unset."""

import logging

import httpx

from app.config import settings
from app.utils.urls import canonicalize_url, is_public_http_url, looks_like_content_url

logger = logging.getLogger("orbit.searxng")

DISCOVERY_QUERIES = [
    "student fellowship applications open",
    "fully funded scholarship applications deadline",
    "developer internship application deadline",
    "open source mentorship program applications",
    "hackathon registration open students",
    "research fellowship for students application",
    "global student competition apply",
]

RELEVANCE_TERMS = (
    "scholarship",
    "internship",
    "fellowship",
    "hackathon",
    "grant",
    "competition",
    "programme",
    "program",
    "mentorship",
    "apply",
    "application",
    "deadline",
    "funded",
    "bursary",
    "residency",
)

NEGATIVE_TERMS = ("login", "signin", "cart", "pricing", "casino", "porn", "job board review")


def is_relevant(title: str, snippet: str, url: str) -> bool:
    """Lightweight relevance classifier — SearXNG results are candidates, not data."""
    blob = f"{title} {snippet} {url}".lower()
    if any(term in blob for term in NEGATIVE_TERMS):
        return False
    hits = sum(1 for term in RELEVANCE_TERMS if term in blob)
    return hits >= 2


async def search(query: str, max_results: int = 10) -> list[dict]:
    if not settings.searxng_enabled:
        return []
    params = {"q": query, "format": "json", "language": "en", "safesearch": "1"}
    try:
        async with httpx.AsyncClient(
            timeout=settings.scraper_timeout,
            headers={"User-Agent": settings.scraper_user_agent},
            follow_redirects=True,
        ) as client:
            resp = await client.get(f"{settings.searxng_base_url}/search", params=params)
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("SearXNG unavailable (%s) — skipping live discovery", exc)
        return []

    out: list[dict] = []
    for item in data.get("results", [])[: max_results * 3]:
        url = canonicalize_url(item.get("url", ""))
        title = item.get("title", "") or ""
        snippet = item.get("content", "") or ""
        if not url or not looks_like_content_url(url):
            continue
        if not is_relevant(title, snippet, url):
            continue
        if not is_public_http_url(url):
            continue
        out.append({"url": url, "title": title, "snippet": snippet})
        if len(out) >= max_results:
            break
    return out
