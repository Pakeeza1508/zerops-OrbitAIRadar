from datetime import datetime
from typing import Literal

from pydantic import Field

from app.models.base import BaseDocument, utcnow


class ScrapeRun(BaseDocument):
    startedAt: datetime = Field(default_factory=utcnow)
    finishedAt: datetime | None = None
    trigger: Literal["cron", "manual"] = "manual"
    sourcesAttempted: int = 0
    sourcesSucceeded: int = 0
    urlsDiscovered: int = 0
    urlsFetched: int = 0
    newCount: int = 0
    updatedCount: int = 0
    duplicateCount: int = 0
    expiredCount: int = 0
    failedCount: int = 0
    aiCalls: int = 0
    status: Literal["running", "success", "partial", "failed"] = "running"
    errors: list[str] = Field(default_factory=list)
