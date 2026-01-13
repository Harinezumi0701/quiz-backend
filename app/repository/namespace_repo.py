# app/repository/namespace_repo.py
from sqlalchemy.orm import Session
from typing import Optional, Tuple, Dict, Any
from app.models.namespaces import Namespace
from app.utils.datetime_utils import datetime_to_timestamp
from app.utils.search_pagination import (
    paginate_query,
    paginate_query_with_multiple_filters,
)


def get_all_namespaces_with_search(
    db: Session,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """Get all namespaces with optional name search and pagination."""
    query = (
        db.query(Namespace)
        .filter(Namespace.deleted_at.is_(None))
        .order_by(Namespace.created_at.desc())
    )

    # Define search configuration
    search_config = {
        "name": {
            "column": Namespace.name,
            "type": "text",
            "case_sensitive": False,
        },
    }

    # Apply search filter and pagination
    if request_params:
        paginated_query, total = paginate_query_with_multiple_filters(
            query,
            request_params=request_params,
            search_config=search_config,
            page=page,
            page_size=page_size,
        )
    else:
        paginated_query, total = paginate_query(
            query,
            search_key=search_key,
            search_value=search_value,
            search_config=search_config,
            page=page,
            page_size=page_size,
        )

    namespaces = paginated_query.all()

    result = []
    for namespace in namespaces:
        result.append(
            {
                "id": namespace.id,
                "name": namespace.name,
                "description": namespace.description,
                "prefix": namespace.prefix,
                "created_at": datetime_to_timestamp(namespace.created_at),
                "updated_at": datetime_to_timestamp(namespace.updated_at),
            }
        )

    return result, total


def get_namespace_by_id(db: Session, namespace_id: str):
    """Get a specific namespace by ID."""
    namespace = (
        db.query(Namespace)
        .filter(Namespace.id == namespace_id, Namespace.deleted_at.is_(None))
        .first()
    )

    if not namespace:
        return None

    return {
        "id": namespace.id,
        "name": namespace.name,
        "description": namespace.description,
        "prefix": namespace.prefix,
        "created_at": datetime_to_timestamp(namespace.created_at),
        "updated_at": datetime_to_timestamp(namespace.updated_at),
    }


def create_namespace(
    db: Session, name: str, prefix: str, description: Optional[str] = None
):
    """
    Create a new namespace.

    Args:
        db: Database session
        name: Namespace name
        prefix: Namespace prefix
        description: Namespace description (optional)

    Returns:
        Namespace dict
    """
    namespace = Namespace(name=name, prefix=prefix, description=description)
    db.add(namespace)
    db.commit()
    db.refresh(namespace)

    return {
        "id": namespace.id,
        "name": namespace.name,
        "description": namespace.description,
        "prefix": namespace.prefix,
        "created_at": datetime_to_timestamp(namespace.created_at),
        "updated_at": datetime_to_timestamp(namespace.updated_at),
    }


def update_namespace(
    db: Session,
    namespace_id: str,
    name: Optional[str] = None,
    prefix: Optional[str] = None,
    description: Optional[str] = None,
):
    """
    Update a namespace.

    Args:
        db: Database session
        namespace_id: Namespace UUID
        name: New namespace name (optional)
        prefix: New namespace prefix (optional)
        description: New namespace description (optional)

    Returns:
        Namespace dict or None if not found
    """
    namespace = (
        db.query(Namespace)
        .filter(Namespace.id == namespace_id, Namespace.deleted_at.is_(None))
        .first()
    )

    if not namespace:
        return None

    if name is not None:
        namespace.name = name
    if prefix is not None:
        namespace.prefix = prefix
    if description is not None:
        namespace.description = description

    db.commit()
    db.refresh(namespace)

    return {
        "id": namespace.id,
        "name": namespace.name,
        "description": namespace.description,
        "prefix": namespace.prefix,
        "created_at": datetime_to_timestamp(namespace.created_at),
        "updated_at": datetime_to_timestamp(namespace.updated_at),
    }


def delete_namespace(db: Session, namespace_id: str):
    """
    Soft delete a namespace.

    Args:
        db: Database session
        namespace_id: Namespace UUID

    Returns:
        bool: True if deleted, False if not found
    """
    from datetime import datetime, timezone

    namespace = (
        db.query(Namespace)
        .filter(Namespace.id == namespace_id, Namespace.deleted_at.is_(None))
        .first()
    )

    if not namespace:
        return False

    namespace.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
