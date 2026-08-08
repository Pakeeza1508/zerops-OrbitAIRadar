from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class OpportunitySearchFilters(BaseModel):
    categories: list[str] = Field(default_factory=list, max_length=20)
    countries: list[str] = Field(default_factory=list, max_length=40)
    skills: list[str] = Field(default_factory=list, max_length=40)
    remote: bool | None = None
    fundingRequired: bool | None = None
    deadlineBefore: datetime | None = None
    deadlineAfter: datetime | None = None
    educationLevels: list[str] = Field(default_factory=list, max_length=20)
    queryText: str | None = Field(default=None, max_length=300)

    @field_validator("categories", "countries", "skills", "educationLevels")
    @classmethod
    def clean_lists(cls, values: list[str]) -> list[str]:
        out, seen = [], set()
        for raw in values or []:
            value = (raw or "").strip()[:80]
            key = value.lower()
            if value and key not in seen:
                seen.add(key)
                out.append(value)
        return out


class AIQueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)


class LiveSearchRequest(BaseModel):
    query: str = Field(default="", max_length=300)
    maxResults: int = Field(default=12, ge=1, le=30)


class SavedUpdateRequest(BaseModel):
    applicationStatus: Literal["saved", "planning", "applied"] | None = None
    notes: str | None = Field(default=None, max_length=2000)


class IngestionRequest(BaseModel):
    query: str | None = Field(default=None, max_length=300)
    maxCandidates: int | None = Field(default=None, ge=1, le=200)


class ScrapeRunResponse(BaseModel):
    id: str | None = None
    startedAt: datetime
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
