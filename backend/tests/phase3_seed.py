"""Disposable Phase 3 E2E fixtures. Never call this against Atlas/production."""
import os
import sys
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

uri = os.getenv("MONGO_URL", "")
db_name = os.getenv("DB_NAME", "")
if not (uri.startswith("mongodb://127.0.0.1:27017") and db_name in {"orbit_phase3_ci", "orbit_phase4_ci"}):
    raise SystemExit("REFUSING to seed a database outside the isolated CI MongoDB service")
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
db = client[db_name]
now = datetime.now(timezone.utc)
fixtures = [
    {
        "title": "Orbit Phase3 Test Fellowship 2027",
        "organization": "Orbit Test Fellowship Lab",
        "category": "fellowship",
        "remote": True,
        "fundingType": "fully_funded",
        "requiredSkills": ["Python"],
        "description": "CI-only fellowship record from an isolated local MongoDB database.",
        "verified": True,
        "verificationStatus": "verified",
        "status": "active",
        "deadline": now + timedelta(days=30),
        "canonicalUrl": "https://example.com/ci-fellowship",
        "sourceUrl": "https://example.com/ci-fellowship",
        "applicationUrl": "https://example.com/ci-fellowship/apply",
        "countriesEligible": ["Global"],
        "locations": ["Remote"],
        "requirements": ["Python"],
        "benefits": ["Mentorship"],
    },
    {
        "title": "Orbit Phase3 Test Internship 2027",
        "organization": "Orbit Test Internship Lab",
        "category": "internship",
        "remote": False,
        "fundingType": "unpaid",
        "requiredSkills": ["JavaScript"],
        "description": "CI-only internship record from an isolated local MongoDB database.",
        "verified": True,
        "verificationStatus": "verified",
        "status": "active",
        "deadline": now + timedelta(days=90),
        "canonicalUrl": "https://example.com/ci-internship",
        "sourceUrl": "https://example.com/ci-internship",
        "applicationUrl": "https://example.com/ci-internship/apply",
        "countriesEligible": ["Pakistan"],
        "locations": ["Lahore"],
        "requirements": ["JavaScript"],
        "benefits": ["Practical experience"],
    }
]
if len(sys.argv) > 1 and sys.argv[1] == "--clear":
    db.opportunities.delete_many({"canonicalUrl": {"$regex": "^https://example.com/ci-"}})
    print("CI fixtures cleared")
else:
    for record in fixtures:
        record.update({"createdAt": now, "updatedAt": now, "lastCheckedAt": now})
        db.opportunities.update_one({"canonicalUrl": record["canonicalUrl"]}, {"$set": record}, upsert=True)
    print("Two isolated E2E opportunities seeded")
