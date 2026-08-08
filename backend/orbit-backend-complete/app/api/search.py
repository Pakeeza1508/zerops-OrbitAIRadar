from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth.debs import get_current_user
from app.models.user import User
from app.schemas.opportunities import AIQueryRequest, LiveSearchRequest, OpportunitySearchFilters
from app.services.ai.groq_client import groq_client
from app.services.ai.tasks import query_to_filters
from app.services.opportunities import list_opportunities
from app.services.scrapper.pipeline import run_ingestion
from app.services.search import deterministic_query_filters

router = APIRouter(prefix="/search", tags=["search"])


def _validated_filters(raw: dict) -> OpportunitySearchFilters:
    allowed = {
        "categories": raw.get("categories") or [],
        "countries": raw.get("countries") or [],
        "skills": raw.get("skills") or [],
        "remote": raw.get("remote"),
        "fundingRequired": raw.get("fundingRequired"),
        "deadlineBefore": raw.get("deadlineBefore"),
        "deadlineAfter": raw.get("deadlineAfter"),
        "educationLevels": raw.get("educationLevels") or [],
        "queryText": raw.get("queryText"),
    }
    return OpportunitySearchFilters.model_validate(allowed)


@router.post("/ai")
async def ai_search(payload: AIQueryRequest, user: User = Depends(get_current_user)):
    raw = await query_to_filters(payload.query)
    used_ai = isinstance(raw, dict)
    if not raw:
        raw = deterministic_query_filters(payload.query)

    try:
        filters = _validated_filters(raw)
    except Exception:
        fallback = deterministic_query_filters(payload.query)
        filters = _validated_filters(fallback)
        raw = fallback
        used_ai = False

    results = await list_opportunities(
        user.id,
        q=filters.queryText,
        categories=filters.categories,
        remote=filters.remote,
        funded=filters.fundingRequired,
        deadline_before=filters.deadlineBefore,
        deadline_after=filters.deadlineAfter,
        countries=filters.countries,
        education_levels=filters.educationLevels,
        skills=filters.skills,
        sort="best_match",
        page=1,
        page_size=50,
    )
    return {
        "answer": raw.get("answer")
        or ("AI interpreted your search." if used_ai else "Search completed with deterministic filters."),
        "filters": filters.model_dump(mode="json"),
        "aiConfigured": groq_client.enabled,
        "usedAI": used_ai,
        **results,
    }


@router.post("/live")
async def live_search(payload: LiveSearchRequest, user: User = Depends(get_current_user)):
    run = await run_ingestion(
        trigger="manual",
        query=payload.query or None,
        max_candidates=max(payload.maxResults, 8),
    )
    results = await list_opportunities(
        user.id,
        q=payload.query or None,
        sort="newest",
        page=1,
        page_size=payload.maxResults,
        include_unverified=True,
    )
    return {
        "run": run,
        "query": payload.query,
        "discoveryCompleted": run.get("status") in {"success", "partial"},
        **results,
    }
