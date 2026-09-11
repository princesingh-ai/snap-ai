from pathlib import Path

from fastmcp import FastMCP
from app.auth.mcp_auth import SnapJWTVerifier

from fastmcp.server.dependencies import get_access_token
from app.auth.rbac import Role, is_allowed

mcp = FastMCP(
    "Snap",
    auth=SnapJWTVerifier(),
)

DATA_ROOT = Path.home() / "snap-data"


def safe_path(relative_path: str) -> Path:
    """Resolve a path while preventing access outside SNAP_DATA_ROOT."""
    root = DATA_ROOT.resolve()
    target = (root / relative_path).resolve()

    if target != root and root not in target.parents:
        raise ValueError(
            "Access outside Snap data directory is not allowed."
        )

    return target


def resource_type_for_path(relative_path: str) -> str:
    """Map a data path to its RBAC resource type."""
    path = Path(relative_path)

    if not path.parts:
        return "public"

    category = path.parts[0].lower()

    mapping = {
        "finance": "finance",
        "policies": "policies",
        "engineering": "engineering",
        "public": "public",
    }

    return mapping.get(category, "public")


@mcp.tool
def search_files(query: str) -> list[str]:
    """Search for authorized files by filename inside the Snap data directory."""

    access_token = get_access_token()

    if access_token is None:
        raise PermissionError("Authentication required.")

    claims = access_token.claims

    try:
        role = Role(claims["role"])
    except (KeyError, ValueError):
        raise PermissionError("Authenticated user has no valid role.")

    if not DATA_ROOT.exists():
        return []

    query = query.lower()
    results = []

    for path in DATA_ROOT.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(DATA_ROOT)
        resource_type = resource_type_for_path(str(relative_path))

        if not is_allowed(role, resource_type, "read"):
            continue

        if query in path.name.lower():
            results.append(str(relative_path))

    return results


@mcp.tool
def read_file(path: str) -> str:
    """Read an authorized text file from the Snap data directory."""

    access_token = get_access_token()

    if access_token is None:
        raise PermissionError("Authentication required.")

    claims = access_token.claims

    try:
        role = Role(claims["role"])
    except (KeyError, ValueError):
        raise PermissionError("Authenticated user has no valid role.")

    target = safe_path(path)
    resource_type = resource_type_for_path(path)

    if not is_allowed(role, resource_type, "read"):
        raise PermissionError(
            f"Role '{role.value}' is not allowed to read "
            f"'{resource_type}' resources."
        )

    if not target.is_file():
        raise FileNotFoundError(path)

    return target.read_text(encoding="utf-8")