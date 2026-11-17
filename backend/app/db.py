import logging
import time
from app.config import connection_diagnostics

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT

from app.config import settings
from app.utils.mongo_dns import configure_mongo_dns

logger = logging.getLogger("orbit.db")

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        meta = connection_diagnostics()
        logger.info("stage=mongo.client_create source=%s target=%s key=%s",
                    meta["mongo_source"], meta["mongo_target"], meta["mongo_key_used"])
        configure_mongo_dns(settings.mongo_url)
        _client = AsyncIOMotorClient(settings.mongo_url, tz_aware=True)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[settings.db_name]


async def ping_db() -> bool:
    started = time.monotonic()
    logger.info("stage=mongo.ping_start")
    try:
        await get_client().admin.command("ping")
        logger.info("stage=mongo.ping_ok elapsed_ms=%d", int((time.monotonic() - started) * 1000))
        return True
    except Exception as exc:
        logger.warning("stage=mongo.ping_failed error_type=%s elapsed_ms=%d",
                       type(exc).__name__, int((time.monotonic() - started) * 1000))
        return False


async def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


async def ensure_indexes() -> None:
    started = time.monotonic()
    logger.info("stage=mongo.indexes_start")
    db = get_db()
    try:
        await db.users.create_index([("email", ASCENDING)], unique=True)
        await db.profiles.create_index([("userId", ASCENDING)], unique=True)

        await db.opportunities.create_index(
            [("canonicalUrl", ASCENDING)],
            unique=True,
            partialFilterExpression={"canonicalUrl": {"$type": "string"}},
        )
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
        logger.info("stage=mongo.indexes_ok elapsed_ms=%d", int((time.monotonic() - started) * 1000))
    except Exception as exc:
        logger.warning("stage=mongo.indexes_failed error_type=%s elapsed_ms=%d",
                       type(exc).__name__, int((time.monotonic() - started) * 1000))
