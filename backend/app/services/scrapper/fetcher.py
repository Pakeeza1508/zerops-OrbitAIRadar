
"""HTTP fetching with polite defaults, robots.txt awareness and optional Crawl4AI.

Crawl4AI / Playwright are imported lazily and only used when plain HTTP is
insufficient, so normal API startup never initialises a browser.
"""

import asyncio
import logging
import urllib.robotparser as robotparser
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from app.config import settings
from app.utils.urls import is_public_http_url

logger = logging.getLogger("orbit.scraper.fetch")

_robots_cache: dict[str, robotparser.RobotFileParser | None] = {}
_domain_locks: dict[str, asyncio.Lock] = {}


@dataclass
class FetchResult:
    url: str
    status: int
    html: str | None
    error: str | None = None
    method: str = "httpx"

    @property
    def ok(self) -> bool:
        return self.status == 200 and bool(self.html)

    @property
    def gone(self) -> bool:
        return self.status in (404, 410)


async def _robots_allowed(url: str) -> bool:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    if base not in _robots_cache:
        parser: robotparser.RobotFileParser | None = robotparser.RobotFileParser()
        parser.set_url(f"{base}/robots.txt")
        try:
            async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
                resp = await client.get(
                    f"{base}/robots.txt", headers={"User-Agent": settings.scraper_user_agent}
                )
            if resp.status_code == 200 and len(resp.text) < 500_000:
                parser.parse(resp.text.splitlines())
            else:
                parser = None
        except httpx.HTTPError:
            parser = None
        _robots_cache[base] = parser
    parser = _robots_cache[base]
    if parser is None:
        return True
    try:
        return parser.can_fetch(settings.scraper_user_agent, url)
    except Exception:
        return True


def _lock_for(url: str) -> asyncio.Lock:
    domain = urlparse(url).netloc
    if domain not in _domain_locks:
        _domain_locks[domain] = asyncio.Lock()
    return _domain_locks[domain]


async def fetch(url: str, crawl_delay: float = 1.0, respect_robots: bool = True) -> FetchResult:
    if not is_public_http_url(url):
        return FetchResult(url=url, status=0, html=None, error="blocked or non-public URL")
    if respect_robots and not await _robots_allowed(url):
        return FetchResult(url=url, status=0, html=None, error="disallowed by robots.txt")

    headers = {
        "User-Agent": settings.scraper_user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with _lock_for(url):
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(
                    timeout=settings.scraper_timeout, follow_redirects=True, headers=headers
                ) as client:
                    resp = await client.get(url)
                await asyncio.sleep(crawl_delay)
                content_type = resp.headers.get("content-type", "")
                if resp.status_code == 200 and (
                    "html" in content_type or "xml" in content_type or not content_type
                ):
                    return FetchResult(url=str(resp.url), status=200, html=resp.text)
                return FetchResult(
                    url=str(resp.url),
                    status=resp.status_code,
                    html=None,
                    error=f"unexpected response ({resp.status_code}, {content_type})",
                )
            except httpx.HTTPError as exc:
                if attempt == 1:
                    return FetchResult(url=url, status=0, html=None, error=str(exc)[:200])
                await asyncio.sleep(1.5)
    return FetchResult(url=url, status=0, html=None, error="unreachable")


async def fetch_rendered(url: str) -> FetchResult:
    """Render with Crawl4AI when plain HTTP yields no usable content.

    Crawl4AI is an optional dependency; if unavailable we degrade gracefully.
    """
    if not is_public_http_url(url):
        return FetchResult(url=url, status=0, html=None, error="blocked URL", method="crawl4ai")
    try:
        from crawl4ai import AsyncWebCrawler  # type: ignore
    except Exception:
        return FetchResult(
            url=url, status=0, html=None, error="crawl4ai not installed", method="crawl4ai"
        )
    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url, bypass_cache=True)
        html = getattr(result, "html", None) or getattr(result, "cleaned_html", None)
        if html:
            return FetchResult(url=url, status=200, html=html, method="crawl4ai")
        return FetchResult(
            url=url, status=0, html=None, error="empty render", method="crawl4ai"
        )
    except Exception as exc:  # pragma: no cover - browser environment dependent
        return FetchResult(url=url, status=0, html=None, error=str(exc)[:200], method="crawl4ai")

