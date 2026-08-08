from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    mongo_url: str = os.getenv("MONGO_URL") or os.getenv("MONGODB_URI") or "mongodb://localhost:27017"
    db_name: str = os.getenv("DB_NAME", "orbit")

    jwt_secret: str = os.getenv("JWT_SECRET", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = _env_int("JWT_EXPIRE_MINUTES", 60 * 24 * 7)

    cors_origins_raw: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    admin_email: str = os.getenv("ADMIN_EMAIL", "").strip().lower()

    groq_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
    groq_model: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
    groq_timeout: float = _env_float("GROQ_TIMEOUT", 30.0)
    max_ai_calls_per_sync: int = _env_int("MAX_AI_CALLS_PER_SYNC", 100)

    searxng_base_url: str = os.getenv("SEARXNG_BASE_URL", "").strip().rstrip("/")

    scraper_timeout: float = _env_float("SCRAPER_TIMEOUT", 20.0)
    scraper_user_agent: str = os.getenv(
        "SCRAPER_USER_AGENT",
        "OrbitOpportunityRadar/1.0 (+https://example.invalid; respectful-public-crawler)",
    )
    scraper_default_delay: float = _env_float("SCRAPER_DEFAULT_DELAY", 1.0)
    max_candidates_per_run: int = _env_int("MAX_CANDIDATES_PER_RUN", 80)
    max_urls_per_source: int = _env_int("MAX_URLS_PER_SOURCE", 20)
    min_ai_extraction_completeness: float = _env_float("MIN_AI_EXTRACTION_COMPLETENESS", 0.50)
    consecutive_gone_threshold: int = _env_int("CONSECUTIVE_GONE_THRESHOLD", 2)
    delete_expired_master: bool = _env_bool("DELETE_EXPIRED_MASTER", True)
    allow_user_manual_ingestion: bool = _env_bool("ALLOW_USER_MANUAL_INGESTION", True)
    manual_ingestion_cooldown_seconds: int = _env_int("MANUAL_INGESTION_COOLDOWN_SECONDS", 60)

    @property
    def cors_origins(self) -> list[str]:
        values = [x.strip() for x in self.cors_origins_raw.split(",") if x.strip()]
        return values or ["http://localhost:3000"]

    @property
    def groq_enabled(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def searxng_enabled(self) -> bool:
        return bool(self.searxng_base_url)


settings = Settings()
