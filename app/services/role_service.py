# app/services/role_service.py
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.constants.error_messages import ERROR_ROLE_ALREADY_EXISTS, ERROR_ROLE_NOT_FOUND
from app.repository import role_repo


def get_role_by_name(db: Session, name: str):
    """Get role by name."""
    return role_repo.get_role_by_name(db, name)


def get_role_by_id(db: Session, role_id: UUID):
    """Get role by ID."""
    role = role_repo.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_ROLE_NOT_FOUND,
        )
    return role


def get_all_roles(db: Session):
    """Get all roles."""
    return role_repo.get_all_roles(db)


def get_all_roles_with_search(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: dict[str, Any] | None = None,
):
    """Get all roles with optional filtering and pagination."""
    return role_repo.get_all_roles_with_search(
        db, page=page, page_size=page_size, request_params=request_params
    )


def create_role(db: Session, name: str, description: str = None):
    """Create a new role."""
    # Check if role already exists
    existing_role = role_repo.get_role_by_name(db, name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ERROR_ROLE_ALREADY_EXISTS,
        )

    return role_repo.create_role(db, name, description)


def add_permission_to_role(db: Session, role_id: UUID, permission: str):
    """Add a permission to a role."""
    role = get_role_by_id(db, role_id)

    # Check if permission already exists
    existing_permissions = role_repo.get_role_permissions(db, role_id)
    for perm in existing_permissions:
        if perm.permission == permission:
            return perm

    return role_repo.add_role_permission(db, role_id, permission)


def remove_permission_from_role(db: Session, role_id: UUID, permission: str):
    """Remove a permission from a role."""
    role = get_role_by_id(db, role_id)
    role_repo.remove_role_permission(db, role_id, permission)


def update_role(db: Session, role_id: UUID, name: str = None, description: str = None):
    """Update a role."""
    # Check if role exists
    role = get_role_by_id(db, role_id)
    
    # Check if new name already exists (if name is being updated)
    if name is not None and name != role.name:
        existing_role = role_repo.get_role_by_name(db, name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ERROR_ROLE_ALREADY_EXISTS,
            )
    
    return role_repo.update_role(db, role_id, name, description)


def delete_role(db: Session, role_id: UUID):
    """Delete a role (soft delete)."""
    role = get_role_by_id(db, role_id)
    deleted = role_repo.delete_role(db, role_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_ROLE_NOT_FOUND,
        )
    return deleted
