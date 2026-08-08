from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from app.auth.debs import client_key, get_current_user, rate_limit
from app.config import settings
from app.db import get_db
from app.models.user import User
from app.schemas.opportunities import IngestionRequest
from app.services.scrapper.pipeline import create_run, get_run, run_ingestion
from app.services.sources import seed_default_sources
from app.utils.mongo import object_id, serialize

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.get("/runs")
async def runs(limit: int = 20, user: User = Depends(get_current_user)):
    docs = await get_db().scrape_runs.find({}).sort("startedAt", -1).limit(min(max(limit, 1), 100)).to_list(100)
    return {"items": [serialize(x) for x in docs]}


@router.get("/runs/{run_id}")
async def run_detail(run_id: str, user: User = Depends(get_current_user)):
    doc = await get_run(run_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return serialize(doc)


@router.get("/sources")
async def sources(user: User = Depends(get_current_user)):
    await seed_default_sources()
    docs = await get_db().sources.find({}).sort("priority", -1).to_list(200)
    return {"items": [serialize(x) for x in docs]}


@router.post("/run")
async def start_run(
    payload: IngestionRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    user: User = Depends(get_current_user),
):
    if not settings.allow_user_manual_ingestion and not user.isAdmin:
        raise HTTPException(status_code=403, detail="Manual discovery is restricted")
    rate_limit(
        client_key(request, f"ingestion:{user.id}"),
        1,
        max(10, settings.manual_ingestion_cooldown_seconds),
    )
    run_id = await create_run("manual")
    background_tasks.add_task(
        run_ingestion,
        "manual",
        payload.query,
        payload.maxCandidates,
        run_id,
    )
    return {"id": run_id, "status": "running", "message": "Discovery run started"}


@router.post("/seed-sources")
async def seed_sources(user: User = Depends(get_current_user)):
    created = await seed_default_sources()
    return {"created": created}
