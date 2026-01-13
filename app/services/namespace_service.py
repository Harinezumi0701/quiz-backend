# app/services/namespace_service.py
from sqlalchemy.orm import Session
from typing import Tuple, Dict, Any, Optional
from app.repository import namespace_repo


def get_all_namespaces_with_search(
    db: Session,
    search_key: str = None,
    search_value: str = None,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """Get all namespaces with optional name search and pagination."""
    return namespace_repo.get_all_namespaces_with_search(
        db, search_key, search_value, page, page_size, request_params
    )


def get_namespace_by_id(db: Session, namespace_id: str):
    """Get a specific namespace by ID."""
    return namespace_repo.get_namespace_by_id(db, namespace_id)


def create_namespace(
    db: Session, name: str, prefix: str, description: Optional[str] = None
):
    """Create a new namespace."""
    return namespace_repo.create_namespace(db, name, prefix, description)


def update_namespace(
    db: Session,
    namespace_id: str,
    name: Optional[str] = None,
    prefix: Optional[str] = None,
    description: Optional[str] = None,
):
    """Update a namespace."""
    return namespace_repo.update_namespace(db, namespace_id, name, prefix, description)


def delete_namespace(db: Session, namespace_id: str):
    """Delete a namespace (soft delete)."""
    return namespace_repo.delete_namespace(db, namespace_id)
