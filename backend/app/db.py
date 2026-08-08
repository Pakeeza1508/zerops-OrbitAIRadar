import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT

from app.config import settings

logger = logging.getLogger("orbit.db")

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_url, tz_aware=True)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[settings.db_name]


async def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


async def ensure_indexes() -> None:
    db = get_db()
    try:
        await db.users.create_index([("email", ASCENDING)], unique=True)
        await db.profiles.create_index([("userId", ASCENDING)], unique=True)

        await db.opportunities.create_index([("canonicalUrl", ASCENDING)], unique=True)
        await db.opportunities.create_index([("fingerprint", ASCENDING)])
        await db.opportunities.create_index([("status", ASCENDING), ("deadline", ASCENDING)])
        await db.opportunities.create_index([("category", ASCENDING)])
        await db.opportunities.create_index([("createdAt", DESCENDING)])
        await db.opportunities.create_index([("organization", ASCENDING)])
        await db.opportunities.create_index([("sourceId", ASCENDING)])
        await db.opportunities.create_index([("contentHash", ASCENDING)])
        await db.opportunities.create_index(
            [
                ("title", TEXT),
                ("organization", TEXT),
                ("description", TEXT),
                ("requiredSkills", TEXT),
            ],
            name="opportunity_text",
            default_language="english",
        )

        await db.saved_opportunities.create_index(
            [("userId", ASCENDING), ("originalOpportunityId", ASCENDING)], unique=True
        )
        await db.saved_opportunities.create_index([("userId", ASCENDING), ("savedAt", DESCENDING)])

        await db.sources.create_index([("baseUrl", ASCENDING)], unique=True)
        await db.scrape_runs.create_index([("startedAt", DESCENDING)])
        await db.locks.create_index([("name", ASCENDING)], unique=True)
        await db.candidate_queue.create_index([("url", ASCENDING)], unique=True)
    except Exception as exc:  # pragma: no cover - index creation is best-effort
        logger.warning("Index creation issue: %s", exc)
