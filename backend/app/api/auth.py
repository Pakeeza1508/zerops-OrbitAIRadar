from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from pymongo.errors import DuplicateKeyError

from app.auth.debs import client_key, get_current_user, rate_limit
from app.auth.security import create_access_token, hash_password, verify_password
from app.db import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, ProfileRequest, RegisterRequest
from app.utils.mongo import serialize

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_response(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "fullName": user.fullName,
        "isAdmin": user.isAdmin,
        "onboardingComplete": user.onboardingComplete,
        "createdAt": user.createdAt.isoformat() if user.createdAt else None,
    }


@router.post("/register")
async def register(payload: RegisterRequest, request: Request):
    rate_limit(client_key(request, "register"), 8, 60)
    db = get_db()
    email = payload.email.lower().strip()
    now = datetime.now(timezone.utc)
    user_doc = {
        "email": email,
        "passwordHash": hash_password(payload.password),
        "fullName": payload.fullName.strip() if payload.fullName else None,
        "isAdmin": False,
        "onboardingComplete": False,
        "createdAt": now,
        "updatedAt": now,
    }
    try:
        result = await db.users.insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user_doc["_id"] = result.inserted_id
    user = User.from_mongo(user_doc)
    await db.profiles.update_one(
        {"userId": str(result.inserted_id)},
        {
            "$setOnInsert": {
                "userId": str(result.inserted_id),
                "fullName": payload.fullName,
                "skills": [],
                "interests": [],
                "preferredCategories": [],
                "locationPreference": [],
                "preferredCountries": [],
                "createdAt": now,
            },
            "$set": {"updatedAt": now},
        },
        upsert=True,
    )
    token = create_access_token(str(result.inserted_id), email)
    return {"accessToken": token, "tokenType": "bearer", "user": _user_response(user)}


@router.post("/login")
async def login(payload: LoginRequest, request: Request):
    rate_limit(client_key(request, "login"), 12, 60)
    db = get_db()
    doc = await db.users.find_one({"email": payload.email.lower().strip()})
    if not doc or not verify_password(payload.password, doc.get("passwordHash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user = User.from_mongo(doc)
    token = create_access_token(str(doc["_id"]), user.email)
    return {"accessToken": token, "tokenType": "bearer", "user": _user_response(user)}


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return _user_response(user)


profile_router = APIRouter(prefix="/profile", tags=["profile"])


@profile_router.get("")
async def get_profile(user: User = Depends(get_current_user)):
    doc = await get_db().profiles.find_one({"userId": user.id})
    if not doc:
        return {
            "userId": user.id,
            "fullName": user.fullName,
            "skills": [],
            "interests": [],
            "preferredCategories": [],
            "locationPreference": [],
            "preferredCountries": [],
        }
    return serialize(doc)


@profile_router.put("")
async def update_profile(payload: ProfileRequest, user: User = Depends(get_current_user)):
    db = get_db()
    now = datetime.now(timezone.utc)
    data = payload.model_dump()
    data.update({"userId": user.id, "updatedAt": now})
    await db.profiles.update_one(
        {"userId": user.id},
        {"$set": data, "$setOnInsert": {"createdAt": now}},
        upsert=True,
    )
    onboarding_complete = bool(
        payload.country
        and payload.educationLevel
        and payload.skills
        and (payload.preferredCategories or payload.interests)
    )
    user_update = {
        "onboardingComplete": onboarding_complete,
        "updatedAt": now,
    }
    if payload.fullName:
        user_update["fullName"] = payload.fullName
    await db.users.update_one({"_id": ObjectId(user.id)}, {"$set": user_update})
    doc = await db.profiles.find_one({"userId": user.id})
    return serialize(doc)
