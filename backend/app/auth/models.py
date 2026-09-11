from pydantic import BaseModel

from app.auth.rbac import Role


class User(BaseModel):
    user_id: str
    username: str
    role: Role