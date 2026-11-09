"""Phase 4: real ingestion with mocked HTTP content, isolated MongoDB ONLY."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Running from frontend/e2e keeps backend imports explicit and isolated.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from unittest.mock import patch
from bson import ObjectId
from httpx import ASGITransport, AsyncClient

from server import app
from app.db import get_db, close_client
from app.services.scrapper.fetcher import FetchResult

URI = os.environ.get("MONGO_URL", "")
NAME = os.environ.get("DB_NAME", "")
if URI != "mongodb://127.0.0.1:27017" or NAME != "orbit_phase4_ci":
    raise SystemExit("REFUSING: Phase 4 tests require disposable local MongoDB only")

SOURCE = "https://phase4-fixture.example.org/list"
DETAIL = "https://phase4-fixture.example.org/fellowship"
TITLE = "Orbit Phase4 Controlled Fellowship 2027"
ADMIN = "phase4-admin-ci@example.com"
NORMAL = "phase4-normal-ci@example.com"
PASSWORD = "Phase4-Isolated-Test-Only-Password-8491"

LISTING = f"""<html><head><title>Controlled Fellowship Listings</title></head>
<body><main><h1>Opportunities</h1><a href="{DETAIL}">Orbit controlled fellowship applications</a></main></body></html>"""
DETAIL_HTML = """<html><head><title>Orbit Phase4 Controlled Fellowship 2027</title>
<meta property="og:site_name" content="Orbit Controlled Test Organization"/>
<meta name="description" content="Fully funded remote research fellowship for international undergraduate Python students. Apply before December 30 2027."/>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"EducationalOccupationalProgram","name":"Orbit Phase4 Controlled Fellowship 2027","description":"Fully funded remote research fellowship for undergraduate Python students worldwide.","provider":{"name":"Orbit Controlled Test Organization"},"applicationDeadline":"2027-12-30"}</script>
</head><body><main><h1>Orbit Phase4 Controlled Fellowship 2027</h1>
<p>Applications are open worldwide. This is a fully funded remote fellowship for undergraduate Computer Science students with Python skills. Deadline: December 30, 2027.</p>
<h2>Requirements</h2><ul><li>Undergraduate students with Python development skills</li></ul>
<h2>Benefits</h2><ul><li>Full mentorship and funded project support</li></ul>
<a href="https://phase4-fixture.example.org/apply">Apply now</a>
</main></body></html>"""

async def fake_fetch(url, *args, **kwargs):
    if url == SOURCE:
        return FetchResult(url=SOURCE, status=200, html=LISTING)
    if url == DETAIL:
        return FetchResult(url=DETAIL, status=200, html=DETAIL_HTML)
    raise AssertionError(f"Unexpected outbound HTTP fetch: {url}")

async def blocked_render(*args, **kwargs):
    raise AssertionError("Unexpected rendered/network fetch in isolated CI")

async def main():
    db = get_db()
    await db.sources.update_many({}, {"$set": {"enabled": False}})
    # Server lifespan may have seeded defaults already. All are disabled here.
    await db.sources.update_one(
        {"baseUrl": SOURCE},
        {"$set": {
            "name": "Phase4 mock-only source", "baseUrl": SOURCE,
            "enabled": True, "discoveryType": "listing", "includeBase": False,
            "allowExternal": False, "category": "fellowship",
            "priority": 100, "crawlDelay": 0.001,
            "updatedAt": datetime.now(timezone.utc),
        }},
        upsert=True,
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        async def create(email):
            r = await client.post("/api/auth/register", json={
                "email": email, "password": PASSWORD, "fullName": "Phase4 isolated user",
            })
            assert r.status_code == 200, (r.status_code, r.text)
            return r.json()["accessToken"]

        admin_jwt = await create(ADMIN)
        user_jwt = await create(NORMAL)
        await db.users.update_one({"email": ADMIN}, {"$set": {"isAdmin": True}})
        headers = lambda token: {"Authorization": f"Bearer {token}"}

        r = await client.get("/api/ingestion/capabilities", headers=headers(user_jwt))
        assert r.status_code == 200 and r.json()["canRunManual"] is False, r.text
        r = await client.get("/api/ingestion/capabilities", headers=headers(admin_jwt))
        assert r.status_code == 200 and r.json()["canRunManual"] is True, r.text

        r = await client.post("/api/ingestion/run", headers=headers(user_jwt), json={"maxCandidates": 1})
        assert r.status_code == 403, ("normal ingestion user", r.status_code, r.text)
        r = await client.post("/api/search/live", headers=headers(user_jwt), json={"maxResults": 1})
        assert r.status_code == 403, ("normal live search user", r.status_code, r.text)
        assert await db.scrape_runs.count_documents({}) == 0, "Denied requests started ingestion"
        print("PHASE4 BACKEND CASE 1 PASS Normal user denied on BOTH ingestion-trigger endpoints")

        # Live search admin route uses its existing implementation, but no crawler
        # call is allowed for this authorization-only assertion.
        async def auth_only_run(*args, **kwargs):
            return {"status": "success", "id": "auth-check-only"}
        with patch("app.api.search.run_ingestion", side_effect=auth_only_run):
            r = await client.post("/api/search/live", headers=headers(admin_jwt), json={"maxResults": 1})
            assert r.status_code == 200, (r.status_code, r.text)
        print("PHASE4 BACKEND CASE 2 PASS Admin authorized for POST /api/search/live")

        # Patch ONLY HTTP response boundary; real discovery, extraction, dedupe,
        # run locking, persistence and pipeline orchestration remain unchanged.
        with patch("app.services.scrapper.discovery.fetch", side_effect=fake_fetch), \
             patch("app.services.scrapper.pipeline.fetch", side_effect=fake_fetch), \
             patch("app.services.scrapper.pipeline.fetch_rendered", side_effect=blocked_render):
            r = await client.post("/api/ingestion/run", headers=headers(admin_jwt),
                                  json={"maxCandidates": 1})
            assert r.status_code == 200, (r.status_code, r.text)
            run_id = r.json()["id"]

        run_result = await client.get(f"/api/ingestion/runs/{run_id}", headers=headers(user_jwt))
        assert run_result.status_code == 200, run_result.text
        run = run_result.json()
        assert run["status"] in ("success", "partial"), run
        assert run["sourcesAttempted"] == 1, run
        assert run["newCount"] == 1, run
        assert run["urlsDiscovered"] == 1, run
        assert run["urlsFetched"] == 1, run
        records = await client.get("/api/opportunities", headers=headers(user_jwt),
                                   params={"q": TITLE})
        assert records.status_code == 200 and records.json()["total"] == 1, records.text
        assert records.json()["items"][0]["title"] == TITLE
        print("PHASE4 BACKEND CASE 3 PASS Real pipeline ingests mocked HTTP source into Discover API")
        print("PHASE4 BACKEND CASE 4 PASS Run record and metrics match actual ingestion")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        try:
            asyncio.run(close_client())
        except Exception:
            pass
