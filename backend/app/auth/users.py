from pwdlib import PasswordHash

from app.auth.models import User
from app.auth.rbac import Role


password_hash = PasswordHash.recommended()


class StoredUser(User):
    password_hash: str


USERS: dict[str, StoredUser] = {}


def add_user(
    user_id: str,
    username: str,
    password: str,
    role: Role,
) -> None:
    if username in USERS:
        raise ValueError(f"User '{username}' already exists.")

    USERS[username] = StoredUser(
        user_id=user_id,
        username=username,
        role=role,
        password_hash=password_hash.hash(password),
    )


def authenticate_user(
    username: str,
    password: str,
) -> User | None:
    user = USERS.get(username)

    if user is None:
        return None

    if not password_hash.verify(password, user.password_hash):
        return None

    return User(
        user_id=user.user_id,
        username=user.username,
        role=user.role,
    )