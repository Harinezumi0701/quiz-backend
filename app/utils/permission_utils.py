# app/utils/permission_utils.py
from typing import Literal

from app.constants.permissions import (
    PERMISSION_ACTION_CREATE,
    PERMISSION_ACTION_DELETE,
    PERMISSION_ACTION_READ,
    PERMISSION_ACTION_UPDATE,
)

HTTPMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


def get_action_from_method(method: str) -> str:
    """
    Map HTTP method to permission action.

    Mapping:
    - GET -> read
    - POST -> create
    - PUT/PATCH -> update
    - DELETE -> delete

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)

    Returns:
        str: Permission action (read, create, update, delete)
    """
    method_upper = method.upper()

    if method_upper == "GET":
        return PERMISSION_ACTION_READ
    elif method_upper == "POST":
        return PERMISSION_ACTION_CREATE
    elif method_upper in ("PUT", "PATCH"):
        return PERMISSION_ACTION_UPDATE
    elif method_upper == "DELETE":
        return PERMISSION_ACTION_DELETE
    else:
        return PERMISSION_ACTION_READ  # Default to read for unknown methods


def build_permission(namespace: str, action: str) -> str:
    """
    Build permission string in format namespace::action.

    Args:
        namespace: Permission namespace (e.g., "category", "role")
        action: Permission action (e.g., "read", "create", "update", "delete")

    Returns:
        str: Permission string in format namespace::action
    """
    return f"{namespace}::{action}"
