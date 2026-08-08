from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.config import settings
from app.services.scrapper.fetcher import fetch
from app.services.searxng import search as searxng_search
from app.utils.urls import canonicalize_url, is_public_http_url, looks_like_content_url

logger = logging.getLogger("orbit.scraper.discovery")

OPPORTUNITY_TERMS = (
    "scholarship", "internship", "fellowship", "hackathon", "grant", "competition",
    "research", "student", "program", "programme", "mentorship", "apply",
    "application", "opportunity", "traineeship", "award",
)


def _candidate_score(text: str, url: str) -> int:
    blob = f"{text} {url}".lower()
    return sum(1 for term in OPPORTUNITY_TERMS if term in blob)


def _allow_candidate(url: str, anchor_text: str, source_url: str, allow_external: bool = False) -> bool:
    if not url or not looks_like_content_url(url):
        return False
    parsed = urlparse(url)
    source = urlparse(source_url)
    same_domain = (
        parsed.netloc.lower().removeprefix("www.")
        == source.netloc.lower().removeprefix("www.")
    )
    if not same_domain and not allow_external:
        return False
    minimum_score = 1 if same_domain else 2
    return _candidate_score(anchor_text, url) >= minimum_score


async def discover_listing(source: dict, max_results: int) -> list[dict]:
    result = await fetch(
        source["baseUrl"],
        crawl_delay=float(source.get("crawlDelay") or settings.scraper_default_delay),
    )
    if not result.ok or not result.html:
        raise RuntimeError(result.error or f"listing fetch failed ({result.status})")
    soup = BeautifulSoup(result.html, "lxml")
    selector = source.get("listingSelector")
    anchors = soup.select(selector) if selector else soup.find_all("a", href=True)
    out, seen = [], set()
    for anchor in anchors:
        href = anchor.get("href") if hasattr(anchor, "get") else None
        if not href:
            continue
        absolute = canonicalize_url(urljoin(result.url, href))
        text = " ".join(anchor.stripped_strings) if hasattr(anchor, "stripped_strings") else ""
        if not absolute or absolute in seen:
            continue
        if not _allow_candidate(
            absolute,
            text,
            result.url,
            bool(source.get("allowExternal")),
        ):
            continue
        if not is_public_http_url(absolute):
            continue
        seen.add(absolute)
        out.append({"url": absolute, "title": text[:180], "sourceType": "listing"})
        if len(out) >= max_results:
            break
    # A source page can itself be a concrete opportunity/program (NASA/Outreachy).
    # Include it so deterministic extraction has a chance to normalize it.
    base = canonicalize_url(result.url)
    if source.get("includeBase") and base and base not in seen:
        out.insert(0, {"url": base, "title": source.get("name", ""), "sourceType": "listing"})
    return out[:max_results]


async def discover_xml(source: dict, max_results: int) -> list[dict]:
    result = await fetch(
        source["baseUrl"],
        crawl_delay=float(source.get("crawlDelay") or settings.scraper_default_delay),
        respect_robots=True,
    )
    if not result.ok or not result.html:
        raise RuntimeError(result.error or f"XML fetch failed ({result.status})")
    try:
        root = ET.fromstring(result.html)
    except ET.ParseError as exc:
        raise RuntimeError(f"invalid XML: {exc}") from exc

    out, seen = [], set()
    dtype = source.get("discoveryType")
    if dtype == "rss":
        nodes = root.findall(".//item") + root.findall(".//{*}entry")
        for node in nodes:
            link = node.findtext("link")
            if not link:
                link_el = node.find("{*}link")
                if link_el is not None:
                    link = link_el.attrib.get("href") or link_el.text
            title = node.findtext("title") or node.findtext("{*}title") or ""
            url = canonicalize_url(urljoin(result.url, link or ""))
            if not url or url in seen or not is_public_http_url(url) or not looks_like_content_url(url):
                continue
            seen.add(url)
            out.append({"url": url, "title": title[:180], "sourceType": "rss"})
            if len(out) >= max_results:
                break
    else:
        for loc in root.findall(".//{*}loc"):
            url = canonicalize_url((loc.text or "").strip())
            if not url or url in seen or not is_public_http_url(url) or not looks_like_content_url(url):
                continue
            if _candidate_score("", url) < 1:
                continue
            seen.add(url)
            out.append({"url": url, "title": "", "sourceType": "sitemap"})
            if len(out) >= max_results:
                break
    return out


async def discover_source(source: dict, max_results: int | None = None) -> list[dict]:
    max_results = max_results or settings.max_urls_per_source
    dtype = source.get("discoveryType", "listing")
    if dtype in {"rss", "sitemap"}:
        return await discover_xml(source, max_results)
    if dtype == "searxng":
        query = (source.get("queries") or [source.get("name", "student opportunities")])[0]
        return [
            {**item, "sourceType": "searxng"}
            for item in await searxng_search(query, max_results=max_results)
        ]
    return await discover_listing(source, max_results)


async def discover_query(query: str, max_results: int = 20) -> list[dict]:
    if settings.searxng_enabled and query.strip():
        items = await searxng_search(query.strip(), max_results=max_results)
        if items:
            return [{**item, "sourceType": "searxng"} for item in items]
    return []
