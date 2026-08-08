from datetime import datetime

from pydantic import EmailStr, Field

from app.models.base import BaseDocument, utcnow


class User(BaseDocument):
    email: EmailStr
    passwordHash: str
    fullName: str | None = None
    isAdmin: bool = False
    onboardingComplete: bool = False
    createdAt: datetime = Field(default_factory=utcnow)
    updatedAt: datetime = Field(default_factory=utcnow)


class Profile(BaseDocument):
    userId: str
    fullName: str | None = None
    country: str | None = None
    educationLevel: str | None = None
    fieldOfStudy: str | None = None
    institution: str | None = None
    graduationYear: int | None = None
    experienceLevel: str | None = None
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    preferredCategories: list[str] = Field(default_factory=list)
    locationPreference: list[str] = Field(default_factory=list)  # remote/hybrid/onsite/global
    preferredCountries: list[str] = Field(default_factory=list)
    fundingPreference: str | None = None  # any | funded_only | unfunded_ok
    createdAt: datetime = Field(default_factory=utcnow)
    updatedAt: datetime = Field(default_factory=utcnow)
