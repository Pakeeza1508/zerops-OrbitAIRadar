"""Duplicate detection: canonical URL first, then organization+title+deadline fingerprint."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.opportunity import Opportunity


async def find_existing(db: AsyncIOMotorDatabase, opportunity: Opportunity) -> dict | None:
    doc = await db.opportunities.find_one({"canonicalUrl": opportunity.canonicalUrl})
    if doc:
        return doc
    if opportunity.fingerprint:
        return await db.opportunities.find_one({"fingerprint": opportunity.fingerprint})
    return None


def is_duplicate_of(existing: dict, opportunity: Opportunity) -> bool:
    """True when the record matches by fingerprint but has a different URL."""
    return (
        bool(existing.get("fingerprint"))
        and existing.get("fingerprint") == opportunity.fingerprint
        and existing.get("canonicalUrl") != opportunity.canonicalUrl
    )
