from fastapi import APIRouter

from app.api.auth import profile_router, router as auth_router
from app.api.ingestion import router as ingestion_router
from app.api.opportunities import router as opportunities_router, stats_router
from app.api.saved import router as saved_router, save_actions_router
from app.api.search import router as search_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(opportunities_router)
api_router.include_router(save_actions_router)
api_router.include_router(saved_router)
api_router.include_router(search_router)
api_router.include_router(stats_router)
api_router.include_router(ingestion_router)


@api_router.get("/")
async def api_root():
    return {
        "name": "Orbit API",
        "status": "ok",
        "version": "1.0.0",
    }
