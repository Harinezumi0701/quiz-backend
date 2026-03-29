# app/api/dependencies/permissions.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.constants.error_messages import ERROR_PERMISSION_DENIED
from app.db.session import get_db
from app.models.users import User
from app.services import permission_service
from app.utils.permission_utils import build_permission, get_action_from_method


def require_permission(permission: str):
    """
    Dependency factory to require a specific permission.

    Usage:
        @router.get("/endpoint")
        def endpoint(user: User = Depends(require_permission("namespace::action"))):
            ...
    """

    def permission_checker(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if not permission_service.check_permission(db, user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_PERMISSION_DENIED,
            )
        return user

    return permission_checker


def require_any_permission(permissions: list[str]):
    """
    Dependency factory to require any of the specified permissions.

    Usage:
        @router.get("/endpoint")
        def endpoint(user: User = Depends(require_any_permission(["namespace1::action1", "namespace2::action2"]))):
            ...
    """

    def permission_checker(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if not permission_service.has_any_permission(db, user, permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_PERMISSION_DENIED,
            )
        return user

    return permission_checker


def require_namespace_permission(namespace: str, method: str = "GET"):
    """
    Dependency factory to require permission based on namespace and HTTP method.
    Automatically maps HTTP method to action (GET->read, POST->create, etc.)

    Usage:
        @router.get("/categories")
        def get_categories(user: User = Depends(require_namespace_permission(PERMISSION_NAMESPACE_CATEGORIES, "GET"))):
            ...

    Args:
        namespace: Permission namespace (e.g., "category", "role")
        method: HTTP method (GET, POST, PUT, PATCH, DELETE). Defaults to "GET"

    Returns:
        Dependency function that checks permission
    """
    action = get_action_from_method(method)
    permission = build_permission(namespace, action)
    return require_permission(permission)
