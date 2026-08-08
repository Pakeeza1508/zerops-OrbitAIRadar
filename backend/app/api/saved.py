from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pymongo import ReturnDocument

from app.auth.debs import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.opportunities import SavedUpdateRequest
from app.services.opportunities import get_opportunity_for_user
from app.utils.mongo import object_id, serialize

router = APIRouter(prefix="/saved", tags=["saved"])


@router.get("")
async def list_saved(user: User = Depends(get_current_user)):
    docs = await get_db().saved_opportunities.find({"userId": user.id}).sort("savedAt", -1).to_list(500)
    items = []
    now = datetime.now(timezone.utc)
    for doc in docs:
        item = serialize(doc)
        snap = item.get("snapshot") or {}
        deadline = snap.get("deadline")
        expired = False
        if deadline:
            try:
                dt = datetime.fromisoformat(deadline.replace("Z", "+00:00")) if isinstance(deadline, str) else deadline
                if dt and dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                expired = bool(dt and dt < now)
            except Exception:
                expired = False
        item["expired"] = bool(item.get("masterDeleted")) or expired
        items.append(item)
    return {"items": items, "total": len(items)}


@router.patch("/{saved_id}")
async def update_saved(
    saved_id: str,
    payload: SavedUpdateRequest,
    user: User = Depends(get_current_user),
):
    oid = object_id(saved_id)
    if not oid:
        raise HTTPException(status_code=404, detail="Saved opportunity not found")
    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    update["updatedAt"] = datetime.now(timezone.utc)
    result = await get_db().saved_opportunities.find_one_and_update(
        {"_id": oid, "userId": user.id},
        {"$set": update},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Saved opportunity not found")
    return serialize(result)


save_actions_router = APIRouter(prefix="/opportunities", tags=["saved"])


@save_actions_router.post("/{opportunity_id}/save")
async def save_opportunity(opportunity_id: str, user: User = Depends(get_current_user)):
    db = get_db()
    item = await get_opportunity_for_user(opportunity_id, user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    now = datetime.now(timezone.utc)

    # Snapshot intentionally excludes ephemeral UI-only values where possible,
    # but retains all factual opportunity fields and the match at save time.
    snapshot = dict(item)
    match_score = int(item.get("matchScore") or 0)
    payload = {
        "userId": user.id,
        "originalOpportunityId": opportunity_id,
        "savedAt": now,
        "applicationStatus": "saved",
        "snapshot": snapshot,
        "snapshotMatchScore": match_score,
        "masterDeleted": False,
        "updatedAt": now,
    }
    await db.saved_opportunities.update_one(
        {"userId": user.id, "originalOpportunityId": opportunity_id},
        {"$set": payload},
        upsert=True,
    )
    doc = await db.saved_opportunities.find_one(
        {"userId": user.id, "originalOpportunityId": opportunity_id}
    )
    return serialize(doc)


@save_actions_router.delete("/{opportunity_id}/save")
async def unsave_opportunity(opportunity_id: str, user: User = Depends(get_current_user)):
    result = await get_db().saved_opportunities.delete_one(
        {"userId": user.id, "originalOpportunityId": opportunity_id}
    )
    return {"removed": bool(result.deleted_count)}
