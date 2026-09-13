from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

from app.auth.mcp_auth import SnapJWTVerifier
from app.auth.rbac import Role, is_allowed


mcp = FastMCP(
    "Snap",
    auth=SnapJWTVerifier(),
)


DATA_ROOT = Path.home() / "snap-data"


def safe_path(relative_path: str) -> Path:
    """
    Resolve a relative path safely inside the Snap data directory.

    Prevents path traversal and rejects paths that resolve outside
    DATA_ROOT.
    """
    root = DATA_ROOT.resolve()
    target = (root / relative_path).resolve()

    if target != root and root not in target.parents:
        raise ValueError(
            "Access outside Snap data directory is not allowed."
        )

    return target


def resource_type_for_path(relative_path: str) -> str:
    """
    Map the first directory component of a data path to its RBAC
    resource type.
    """
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
    """
    Search the authenticated user's authorized organizational files
    by filename.

    Use this tool when the user asks to find an internal company file
    or when a file needs to be located before reading it.

    The search is performed only inside the configured Snap data
    directory. Results are filtered according to the authenticated
    user's role and RBAC permissions.

    Args:
        query:
            A short filename or filename fragment to search for.

            Examples:
            - "main.cpp"
            - "architecture"
            - "revenue"
            - "policy"

    Returns:
        A list of relative file paths that the authenticated user is
        authorized to access.

        An empty list means that no matching authorized files were
        found.

    Important:
        This tool searches filenames, not file contents.
        Use read_file() after locating a file when its contents
        are required.
    """
    access_token = get_access_token()

    if access_token is None:
        raise PermissionError("Authentication required.")

    claims = access_token.claims

    try:
        role = Role(claims["role"])
    except (KeyError, ValueError):
        raise PermissionError(
            "Authenticated user has no valid role."
        )

    if not DATA_ROOT.exists():
        return []

    query = query.lower().strip()

    if not query:
        return []

    results = []

    for path in DATA_ROOT.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(DATA_ROOT)

        resource_type = resource_type_for_path(
            str(relative_path)
        )

        if not is_allowed(
            role,
            resource_type,
            "read",
        ):
            continue

        if query in path.name.lower():
            results.append(str(relative_path))

    return results


@mcp.tool
def read_file(path: str) -> str:
    """
    Read an authorized internal organizational text file.

    Use this tool after search_files() identifies a relevant file,
    or when the user provides the path to a specific internal file.

    Access is controlled by the authenticated user's role and the
    RBAC permissions associated with the resource category.

    Args:
        path:
            Relative path to a file inside the Snap data directory.

            Examples:
            - "engineering/main.cpp"
            - "engineering/architecture.txt"
            - "finance/revenue.txt"
            - "policies/security-policy.txt"

    Returns:
        The UTF-8 text contents of the requested file.

    Raises:
        PermissionError:
            If authentication is missing, the user's role is invalid,
            or the user does not have permission to access the resource.

        FileNotFoundError:
            If the requested file does not exist.

        ValueError:
            If the requested path attempts to escape the Snap data
            directory.

    Important:
        This tool is restricted to the configured Snap data directory.
        It does not provide general filesystem access.
    """
    access_token = get_access_token()

    if access_token is None:
        raise PermissionError("Authentication required.")

    claims = access_token.claims

    try:
        role = Role(claims["role"])
    except (KeyError, ValueError):
        raise PermissionError(
            "Authenticated user has no valid role."
        )

    target = safe_path(path)

    resource_type = resource_type_for_path(path)

    if not is_allowed(
        role,
        resource_type,
        "read",
    ):
        raise PermissionError(
            f"Role '{role.value}' is not allowed to read "
            f"'{resource_type}' resources."
        )

    if not target.is_file():
        raise FileNotFoundError(path)

    return target.read_text(
        encoding="utf-8"
    )