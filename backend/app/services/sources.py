from __future__ import annotations

from datetime import datetime, timezone

from app.db import get_db

DEFAULT_SOURCES = [
    {
        "name": "NASA Internship Programs",
        "baseUrl": "https://www.nasa.gov/learning-resources/internship-programs/",
        "category": "internship",
        "enabled": True,
        "discoveryType": "listing",
        "includeBase": True,
        "priority": 10,
        "crawlDelay": 1.5,
    },
    {
        "name": "Outreachy Apply",
        "baseUrl": "https://www.outreachy.org/apply/",
        "category": "open_source",
        "enabled": True,
        "discoveryType": "listing",
        "includeBase": True,
        "priority": 10,
        "crawlDelay": 1.5,
    },
    {
        "name": "Outreachy Home",
        "baseUrl": "https://www.outreachy.org/",
        "category": "open_source",
        "enabled": True,
        "discoveryType": "listing",
        "priority": 9,
        "crawlDelay": 1.5,
    },
    {
        "name": "Erasmus+ Opportunities",
        "baseUrl": "https://erasmus-plus.ec.europa.eu/opportunities/individuals",
        "category": "scholarship",
        "enabled": True,
        "discoveryType": "listing",
        "priority": 8,
        "crawlDelay": 1.5,
    },
    {
        "name": "DAAD Scholarship Database",
        "baseUrl": "https://www2.daad.de/deutschland/stipendium/datenbank/en/21148-scholarship-database/?daad=1",
        "category": "scholarship",
        "enabled": True,
        "discoveryType": "listing",
        "priority": 8,
        "crawlDelay": 1.5,
    },
    {
        "name": "CERN Students",
        "baseUrl": "https://careers.cern/programmes/",
        "category": "research",
        "enabled": True,
        "discoveryType": "listing",
        "priority": 8,
        "crawlDelay": 1.5,
    },
    {
        "name": "Google Summer of Code 2026",
        "baseUrl": "https://summerofcode.withgoogle.com/programs/2026",
        "category": "open_source",
        "enabled": True,
        "discoveryType": "listing",
        "includeBase": True,
        "priority": 8,
        "crawlDelay": 1.5,
    },
    {
        "name": "MLH Events",
        "baseUrl": "https://mlh.io/seasons/2026/events",
        "category": "hackathon",
        "enabled": True,
        "discoveryType": "listing",
        "allowExternal": True,
        "priority": 7,
        "crawlDelay": 1.5,
    },
]


async def seed_default_sources() -> int:
    db = get_db()
    now = datetime.now(timezone.utc)
    created = 0
    for source in DEFAULT_SOURCES:
        # Do not overwrite operational/admin choices (enabled, priority, crawlDelay)
        # on every startup. Seed defaults only when the source is first created, while
        # refreshing the canonical name/category metadata for existing rows.
        insert_payload = {
            "baseUrl": source["baseUrl"],
            "enabled": source.get("enabled", True),
            "includeBase": source.get("includeBase", False),
            "allowExternal": source.get("allowExternal", False),
            "priority": source.get("priority", 5),
            "crawlDelay": source.get("crawlDelay", 1.5),
            "listingSelector": source.get("listingSelector"),
            "queries": source.get("queries", []),
            "createdAt": now,
            "consecutiveFailures": 0,
        }
        result = await db.sources.update_one(
            {"baseUrl": source["baseUrl"]},
            {
                "$set": {
                    "name": source["name"],
                    "category": source.get("category", "other"),
                    "discoveryType": source.get("discoveryType", "listing"),
                    "updatedAt": now,
                },
                "$setOnInsert": insert_payload,
            },
            upsert=True,
        )
        if result.upserted_id:
            created += 1
    return created
