from datetime import datetime

from pydantic import Field

from app.models.base import BaseDocument, utcnow


class Source(BaseDocument):
    name: str
    baseUrl: str
    category: str = "other"
    enabled: bool = True
    discoveryType: str = "rss"  # rss | sitemap | listing | searxng
    listingSelector: str | None = None
    queries: list[str] = Field(default_factory=list)
    lastRunAt: datetime | None = None
    lastSuccessAt: datetime | None = None
    consecutiveFailures: int = 0
    lastError: str | None = None
    crawlDelay: float = 1.5
    priority: int = 5
    createdAt: datetime = Field(default_factory=utcnow)
    updatedAt: datetime = Field(default_factory=utcnow)
