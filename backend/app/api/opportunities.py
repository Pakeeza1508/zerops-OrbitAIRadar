from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.debs import get_current_user
from app.models.user import User
from app.services.ai.tasks import explain_match
from app.services.opportunities import (
    dashboard_stats,
    get_opportunity_for_user,
    get_profile,
    list_opportunities,
)

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


def _split_csv(value: str | None) -> list[str]:
    return [x.strip() for x in (value or "").split(",") if x.strip()]


@router.get("")
async def opportunities(
    q: str | None = Query(default=None, max_length=200),
    category: str | None = None,
    remote: bool | None = None,
    funded: bool | None = None,
    deadlineBefore: datetime | None = None,
    deadlineAfter: datetime | None = None,
    countries: str | None = None,
    education: str | None = None,
    skills: str | None = None,
    minMatch: int = Query(default=0, ge=0, le=100),
    sort: str = Query(default="best_match", pattern="^(best_match|newest|deadline)$"),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    includeUnverified: bool = False,
    user: User = Depends(get_current_user),
):
    return await list_opportunities(
        user.id,
        q=q,
        categories=_split_csv(category),
        remote=remote,
        funded=funded,
        deadline_before=deadlineBefore,
        deadline_after=deadlineAfter,
        countries=_split_csv(countries),
        education_levels=_split_csv(education),
        skills=_split_csv(skills),
        min_match=minMatch,
        sort=sort,
        page=page,
        page_size=pageSize,
        include_unverified=includeUnverified,
    )


@router.get("/{opportunity_id}")
async def opportunity_detail(
    opportunity_id: str,
    explainAI: bool = False,
    user: User = Depends(get_current_user),
):
    item = await get_opportunity_for_user(opportunity_id, user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if explainAI:
        profile_doc = await get_profile(user.id)
        explanation = await explain_match(item, profile_doc, item.get("match", {}))
        item["aiExplanation"] = explanation
    return item


stats_router = APIRouter(prefix="/stats", tags=["stats"])


@stats_router.get("")
async def stats(user: User = Depends(get_current_user)):
    return await dashboard_stats(user.id)
