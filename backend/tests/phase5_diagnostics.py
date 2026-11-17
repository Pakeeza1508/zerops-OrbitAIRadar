"""Phase 5 targeted diagnostics: safe startup, CORS and MongoDB error behavior.

This suite must run only against the isolated GitHub Actions database/environment.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path
from unittest.mock import patch
import dns.resolver

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.utils import mongo_dns

from httpx import ASGITransport, AsyncClient
from pymongo.errors import ServerSelectionTimeoutError
from app.config import connection_diagnostics, settings
from server import app

assert os.environ.get("DB_NAME") == "orbit_phase4_ci", "Refusing non-test DB"
assert os.environ.get("MONGO_URL") == "mongodb://127.0.0.1:27017", "Refusing non-local MongoDB"

class BrokenCollection:
    async def insert_one(self, value):
        raise ServerSelectionTimeoutError("synthetic test-only MongoDB offline")

class BrokenDb:
    users = BrokenCollection()

async def main():
    meta = connection_diagnostics()
    assert meta["mongo_key_used"] == "MONGO_URL", meta
    assert meta["mongo_source"] == "process_environment", meta
    assert meta["mongo_target"] == "local", meta
    assert "mongodb://" not in str(meta)
    print("PHASE5 DIAGNOSTICS CASE 1 PASS Safe configuration provenance; no URI")

    saved_resolver = dns.resolver.default_resolver
    saved_configured = mongo_dns._configured
    try:
        with patch("app.utils.mongo_dns.platform.system", return_value="Windows"):
            mongo_dns._configured = False
            with patch.dict(os.environ, {"MONGO_DNS_SERVERS": ""}):
                mongo_dns.configure_mongo_dns("mongodb+srv://test.example.com/")
                assert list(dns.resolver.get_default_resolver().nameservers) == ["1.1.1.1", "1.0.0.1"]
            # A subsequent MongoDB call must not reset the configured DNS resolver.
            mongo_dns.configure_mongo_dns("mongodb+srv://test.example.com/")
            assert list(dns.resolver.get_default_resolver().nameservers) == ["1.1.1.1", "1.0.0.1"]
        print("PHASE5 DIAGNOSTICS CASE 1B PASS Windows SRV DNS auto configuration")
    finally:
        dns.resolver.default_resolver = saved_resolver
        mongo_dns._configured = saved_configured

    with patch("app.utils.mongo_dns.platform.system", return_value="Linux"):
        mongo_dns._configured = False
        with patch.dict(os.environ, {"MONGO_DNS_SERVERS": ""}):
            mongo_dns.configure_mongo_dns("mongodb+srv://test.example.com/")
            assert dns.resolver.default_resolver is saved_resolver
        mongo_dns._configured = saved_configured
    print("PHASE5 DIAGNOSTICS CASE 1C PASS Hosting system DNS unchanged")


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        allowed = await client.options("/api/auth/register", headers={
            "Origin": settings.cors_origins[0],
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        })
        assert allowed.status_code == 200, (allowed.status_code, allowed.text)
        assert allowed.headers.get("access-control-allow-origin") == settings.cors_origins[0]
        denied = await client.options("/api/auth/register", headers={
            "Origin": "https://not-allowed.example.invalid",
            "Access-Control-Request-Method": "POST",
        })
        assert denied.status_code == 400, (denied.status_code, denied.text)
        print("PHASE5 DIAGNOSTICS CASE 2 PASS CORS allowed vs disallowed origin")

        with patch("app.api.auth.get_db", return_value=BrokenDb()):
            response = await client.post("/api/auth/register", json={
                "email": "phase5-offline@example.com",
                "password": "Diagnostics-Test-Only-Passphrase-1234",
                "fullName": "Phase 5 Diagnostics",
            })
        assert response.status_code == 503, (response.status_code, response.text)
        assert "Database unavailable" in response.json().get("detail", "")
        print("PHASE5 DIAGNOSTICS CASE 3 PASS Offline Mongo returns controlled 503")

if __name__ == "__main__":
    asyncio.run(main())
