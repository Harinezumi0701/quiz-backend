# app/services/permission_service.py
import fnmatch
from sqlalchemy.orm import Session
from app.models.users import User
from app.repository import role_repo


def check_permission(db: Session, user: User, required_permission: str) -> bool:
    """
    Check if user has the required permission.

    Permission format: <namespace>::<action>
    Wildcard support: *::* (all permissions), namespace::* (all actions in namespace), *::action (all namespaces with action)

    Args:
        db: Database session
        user: User object
        required_permission: Required permission in format namespace::action

    Returns:
        bool: True if user has permission, False otherwise
    """
    # If user has no role_id, they have no permissions
    if not user.role_id:
        return False

    # Get role with permissions
    role = role_repo.get_role_by_id(db, user.role_id)
    if not role:
        return False

    # Get all permissions for the role
    role_permissions = role_repo.get_role_permissions(db, user.role_id)

    # Check if any permission matches the required permission
    for role_perm in role_permissions:
        if _permission_matches(role_perm.permission, required_permission):
            return True

    return False


def _permission_matches(pattern: str, permission: str) -> bool:
    """
    Check if a permission pattern matches a required permission.

    Supports wildcards:
    - *::* matches everything
    - namespace::* matches all actions in namespace
    - *::action matches action in all namespaces
    - namespace::action matches exact permission
    """
    # Exact match
    if pattern == permission:
        return True

    # Wildcard match: *::*
    if pattern == "*::*":
        return True

    # Split pattern and permission
    try:
        pattern_parts = pattern.split("::")
        perm_parts = permission.split("::")

        if len(pattern_parts) != 2 or len(perm_parts) != 2:
            return False

        pattern_namespace, pattern_action = pattern_parts
        perm_namespace, perm_action = perm_parts

        # namespace::* matches all actions in namespace
        if pattern_namespace == perm_namespace and pattern_action == "*":
            return True

        # *::action matches action in all namespaces
        if pattern_namespace == "*" and pattern_action == perm_action:
            return True

        # Use fnmatch for more flexible matching
        if fnmatch.fnmatch(perm_namespace, pattern_namespace) and fnmatch.fnmatch(
            perm_action, pattern_action
        ):
            return True

    except Exception:
        return False

    return False


def has_any_permission(
    db: Session, user: User, required_permissions: list[str]
) -> bool:
    """
    Check if user has any of the required permissions.

    Args:
        db: Database session
        user: User object
        required_permissions: List of required permissions

    Returns:
        bool: True if user has at least one permission, False otherwise
    """
    for permission in required_permissions:
        if check_permission(db, user, permission):
            return True
    return False


def get_user_permissions(db: Session, user: User) -> list[str]:
    """
    Get all permissions for a user based on their role.

    Args:
        db: Database session
        user: User object

    Returns:
        list[str]: List of permission strings (e.g., ["category::read", "*::*"])
    """
    if not user.role_id:
        return []

    role_permissions = role_repo.get_role_permissions(db, user.role_id)
    return [perm.permission for perm in role_permissions]
