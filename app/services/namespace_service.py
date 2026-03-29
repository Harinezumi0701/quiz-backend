# app/services/namespace_service.py
from typing import Any

from sqlalchemy.orm import Session

from app.repository import namespace_repo


def get_all_namespaces_with_search(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: dict[str, Any] | None = None,
) -> tuple[list, int]:
    """Get all namespaces with optional name search and pagination."""
    return namespace_repo.get_all_namespaces_with_search(
        db, page=page, page_size=page_size, request_params=request_params
    )


def get_namespace_by_id(db: Session, namespace_id: str):
    """Get a specific namespace by ID."""
    return namespace_repo.get_namespace_by_id(db, namespace_id)


def create_namespace(
    db: Session, name: str, prefix: str, description: str | None = None
):
    """Create a new namespace."""
    return namespace_repo.create_namespace(db, name, prefix, description)


def update_namespace(
    db: Session,
    namespace_id: str,
    name: str | None = None,
    prefix: str | None = None,
    description: str | None = None,
):
    """Update a namespace."""
    return namespace_repo.update_namespace(db, namespace_id, name, prefix, description)


def delete_namespace(db: Session, namespace_id: str):
    """Delete a namespace (soft delete)."""
    return namespace_repo.delete_namespace(db, namespace_id)
