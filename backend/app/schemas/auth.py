from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    fullName: str | None = Field(default=None, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    fullName: str | None = None
    isAdmin: bool = False
    onboardingComplete: bool = False
    createdAt: datetime | None = None


class ProfileRequest(BaseModel):
    fullName: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=80)
    educationLevel: str | None = Field(default=None, max_length=60)
    fieldOfStudy: str | None = Field(default=None, max_length=120)
    institution: str | None = Field(default=None, max_length=160)
    graduationYear: int | None = Field(default=None, ge=1950, le=2100)
    experienceLevel: str | None = Field(default=None, max_length=40)
    skills: list[str] = Field(default_factory=list, max_length=60)
    interests: list[str] = Field(default_factory=list, max_length=40)
    preferredCategories: list[str] = Field(default_factory=list, max_length=20)
    locationPreference: list[str] = Field(default_factory=list, max_length=10)
    preferredCountries: list[str] = Field(default_factory=list, max_length=40)
    fundingPreference: str | None = Field(default=None, max_length=30)

    @field_validator("skills", "interests", "preferredCategories", "preferredCountries")
    @classmethod
    def clean_list(cls, values: list[str]) -> list[str]:
        seen, out = set(), []
        for v in values:
            v = (v or "").strip()[:60]
            if v and v.lower() not in seen:
                seen.add(v.lower())
                out.append(v)
        return out


class ProfileResponse(ProfileRequest):
    userId: str
    updatedAt: datetime | None = None


TokenResponse.model_rebuild()
