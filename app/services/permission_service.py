# app/services/permission_service.py
import fnmatch
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Any, Optional, Tuple
from fastapi import HTTPException, status
from app.models.users import User
from app.repository import role_repo
from app.repository import permission_repo
from app.constants.permissions import (
    PERMISSION_NAMESPACE_CATEGORIES,
    PERMISSION_ACTION_READ,
    PERMISSION_WILDCARD_ALL,
    DEFAULT_USER_PERMISSIONS,
)


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
    # If user has no role_id, check against default permissions
    if not user.role_id:
        for default_perm in DEFAULT_USER_PERMISSIONS:
            if _permission_matches(default_perm, required_permission):
                return True
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
    Users without a role get default permissions.

    Args:
        db: Database session
        user: User object

    Returns:
        list[str]: List of permission strings (e.g., [f"{PERMISSION_NAMESPACE_CATEGORIES}::{PERMISSION_ACTION_READ}", PERMISSION_WILDCARD_ALL])
    """
    if not user.role_id:
        return DEFAULT_USER_PERMISSIONS.copy()

    role_permissions = role_repo.get_role_permissions(db, user.role_id)
    return [perm.permission for perm in role_permissions]


def get_all_permissions(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """Get all permissions with optional filtering and pagination."""
    return permission_repo.get_all_permissions(
        db, page=page, page_size=page_size, request_params=request_params
    )


def get_permission_by_id(db: Session, permission_id: UUID):
    """Get permission by ID."""
    permission = permission_repo.get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with ID {permission_id} not found",
        )
    return permission


def create_permission(
    db: Session, role_id: UUID, permission: str, name: str = None, description: str = None
):
    """Create a new permission."""
    # Check if permission already exists for this role
    existing_permissions = role_repo.get_role_permissions(db, role_id)
    for perm in existing_permissions:
        if perm.permission == permission:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission '{permission}' already exists for this role",
            )
    
    permission_obj = permission_repo.create_permission(
        db, role_id, permission, name, description
    )
    if not permission_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found",
        )
    return permission_obj


def update_permission(
    db: Session,
    permission_id: UUID,
    role_id: UUID = None,
    permission: str = None,
    name: str = None,
    description: str = None,
):
    """Update a permission."""
    # Check if permission already exists for the role (if role_id is being updated)
    if role_id is not None and permission is not None:
        existing_permissions = role_repo.get_role_permissions(db, role_id)
        for perm in existing_permissions:
            if perm.permission == permission and perm.id != permission_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Permission '{permission}' already exists for this role",
                )
    
    permission_obj = permission_repo.update_permission(
        db, permission_id, role_id, permission, name, description
    )
    if not permission_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with ID {permission_id} not found",
        )
    return permission_obj


def delete_permission(db: Session, permission_id: UUID):
    """Delete a permission."""
    deleted = permission_repo.delete_permission(db, permission_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with ID {permission_id} not found",
        )
    return deleted
