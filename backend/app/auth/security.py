import secrets
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError

from app.config import settings

_hasher = PasswordHasher()

# Fallback secret is generated per-process so tokens never validate across
# restarts if JWT_SECRET was not configured. Production must set JWT_SECRET.
_RUNTIME_SECRET = settings.jwt_secret or secrets.token_urlsafe(48)


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, ValueError):
        return False


def create_access_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    return jwt.encode(payload, _RUNTIME_SECRET, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, _RUNTIME_SECRET, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
