
import time
from collections import defaultdict, deque

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.security import decode_access_token
from app.config import settings
from app.db import get_db
from app.models.user import User

bearer = HTTPBearer(auto_error=False)

_buckets: dict[str, deque] = defaultdict(deque)


def rate_limit(key: str, limit: int, window_seconds: int) -> None:
    """Simple in-process sliding-window rate limiter."""
    now = time.time()
    bucket = _buckets[key]
    while bucket and now - bucket[0] > window_seconds:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down.",
        )
    bucket.append(now)


def client_key(request: Request, suffix: str) -> str:
    ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
        request.client.host if request.client else "unknown"
    )
    return f"{suffix}:{ip}"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        oid = ObjectId(payload["sub"])
    except (InvalidId, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token subject")
    doc = await get_db().users.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return User.from_mongo(doc)


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.isAdmin or (settings.admin_email and user.email.lower() == settings.admin_email):
        return user
    raise HTTPException(status_code=403, detail="Admin privileges required")

