from enum import StrEnum


class Role(StrEnum):
    VIEWER = "viewer"
    ENGINEERING = "engineering"
    FINANCE = "finance"
    OPERATOR = "operator"
    ADMIN = "admin"


ROLE_PERMISSIONS = {
    Role.VIEWER: {
        "public.read",
        "policies.read",
    },

    Role.ENGINEERING: {
        "public.read",
        "policies.read",
        "engineering.read",
    },

    Role.FINANCE: {
        "public.read",
        "policies.read",
        "finance.read",
    },

    Role.OPERATOR: {
        "public.read",
        "policies.read",
        "engineering.read",
        "finance.read",
    },

    Role.ADMIN: {
        "*",
    },
}


def is_allowed(
    role: Role,
    resource_type: str,
    action: str,
) -> bool:

    permissions = ROLE_PERMISSIONS.get(role, set())

    if "*" in permissions:
        return True

    return f"{resource_type}.{action}" in permissions