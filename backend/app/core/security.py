import datetime as dt
from typing import Any

import jwt

from app.core.config import settings


def create_access_token(subject: str, role: str, expires_delta: dt.timedelta | None = None) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    expire = now + (expires_delta or dt.timedelta(minutes=settings.access_token_expire_minutes))
    payload = {
        "sub": str(subject),
        "role": role,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])