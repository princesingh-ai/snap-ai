import jwt

from fastmcp.server.auth import AccessToken, TokenVerifier

from app.auth.rbac import Role
from app.config.settings import settings


class SnapJWTVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )

            user_id = payload["sub"]
            username = payload["username"]
            role = Role(payload["role"])

        except (
            jwt.InvalidTokenError,
            KeyError,
            ValueError,
        ):
            return None

        return AccessToken(
            token=token,
            client_id=username,
            scopes=[],
            expires_at=payload.get("exp"),
            subject=user_id,
            claims={
                "user_id": user_id,
                "username": username,
                "role": role.value,
            },
        )