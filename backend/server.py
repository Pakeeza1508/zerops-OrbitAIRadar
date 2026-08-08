from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.db import close_client, ensure_indexes, ping_db
from app.services.sources import seed_default_sources
from app.utils.logging import setup_logging

setup_logging()
logger = logging.getLogger("orbit.server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await ensure_indexes()
        await seed_default_sources()
    except Exception as exc:
        # App can still start so health/logs expose configuration issues instead
        # of crashing the preview process immediately.
        logger.warning("Startup initialization issue: %s", exc)
    yield
    await close_client()


app = FastAPI(
    title="Orbit — AI Opportunity Radar",
    version="1.0.0",
    lifespan=lifespan,
)

cors_origins = settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_credentials="*" not in cors_origins,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    database_ok = await ping_db()
    return {
        "status": "ok" if database_ok else "degraded",
        "database": "connected" if database_ok else "unavailable",
        "groqConfigured": settings.groq_enabled,
        "searxngConfigured": settings.searxng_enabled,
    }


@app.get("/ready")
async def ready(response: Response):
    database_ok = await ping_db()
    if not database_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"ready": database_ok, "database": "connected" if database_ok else "unavailable"}


@app.get("/")
async def root():
    return {
        "name": "Orbit — AI Opportunity Radar",
        "api": "/api",
        "health": "/health",
    }
