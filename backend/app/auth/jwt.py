from datetime import datetime, timedelta, timezone

import jwt

from app.auth.models import User
from app.auth.rbac import Role
from app.config.settings import settings


def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )

    payload = {
        "sub": user.user_id,
        "username": user.username,
        "role": user.role.value,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> User:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    return User(
        user_id=payload["sub"],
        username=payload["username"],
        role=Role(payload["role"]),
    )