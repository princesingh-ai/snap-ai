from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.rbac import is_allowed


def require_permission(resource_type: str, action: str):
    def dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if not is_allowed(
            current_user.role,
            resource_type,
            action,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied.",
            )

        return current_user

    return dependency