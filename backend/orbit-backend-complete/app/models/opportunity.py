
from datetime import datetime
from typing import Literal

from pydantic import Field

from app.models.base import BaseDocument, utcnow

CATEGORIES = [
    "scholarship",
    "internship",
    "fellowship",
    "hackathon",
    "grant",
    "competition",
    "research",
    "open_source",
    "developer_program",
    "mentorship",
    "other",
]

OpportunityStatus = Literal["active", "closing_soon", "expired", "closed", "unverified"]
VerificationStatus = Literal["verified", "likely_verified", "unverified"]


class Opportunity(BaseDocument):
    title: str
    organization: str | None = None
    slug: str | None = None
    description: str | None = None
    shortDescription: str | None = None
    category: str = "other"

    sourceUrl: str
    applicationUrl: str | None = None
    canonicalUrl: str
    sourceDomain: str | None = None

    countriesEligible: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    remote: bool | None = None
    hybrid: bool | None = None
    onsite: bool | None = None

    educationLevels: list[str] = Field(default_factory=list)
    fieldsOfStudy: list[str] = Field(default_factory=list)
    requiredSkills: list[str] = Field(default_factory=list)
    preferredSkills: list[str] = Field(default_factory=list)
    experienceLevels: list[str] = Field(default_factory=list)

    fundingType: str | None = None
    fundingAmount: float | None = None
    currency: str | None = None

    deadline: datetime | None = None
    deadlineText: str | None = None
    applicationOpenDate: datetime | None = None

    eligibilityText: str | None = None
    requirements: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)

    verified: bool = False
    verificationStatus: VerificationStatus = "unverified"
    sourceType: str | None = None
    extractionMethod: str | None = None
    aiConfidence: float | None = None
    isDemoData: bool = False

    status: OpportunityStatus = "active"

    scrapedAt: datetime = Field(default_factory=utcnow)
    lastSeenAt: datetime = Field(default_factory=utcnow)
    lastCheckedAt: datetime = Field(default_factory=utcnow)
    lastChangedAt: datetime = Field(default_factory=utcnow)

    contentHash: str | None = None
    fingerprint: str | None = None
    consecutiveFetchFailures: int = 0

    sourceId: str | None = None

    createdAt: datetime = Field(default_factory=utcnow)
    updatedAt: datetime = Field(default_factory=utcnow)

