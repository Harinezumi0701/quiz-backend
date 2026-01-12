# app/repository/user_repo.py
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, Tuple, Dict, Any
from app.models.users import User
from app.utils.search_pagination import (
    paginate_query,
    paginate_query_with_multiple_filters,
)


def get_all_users(
    db: Session,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """Get all users with optional filtering and pagination."""
    query = db.query(User)

    # Define search configuration
    search_config = {
        "full_name": {
            "column": User.full_name,
            "type": "text",
            "case_sensitive": False,
        },
        "user_id": {
            "column": User.user_id,
            "type": "text",
            "case_sensitive": False,
        },
        "email": {
            "column": User.email,
            "type": "text",
            "case_sensitive": False,
        },
        "phone": {
            "column": User.phone,
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

    return paginated_query.all(), total


def get_user_by_id(db: Session, user_id: UUID):
    """Get user by UUID id."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_user_id(db: Session, user_id: str):
    """Get user by user_id (editable unique identifier)."""
    return db.query(User).filter(User.user_id == user_id).first()


def user_id_exists(db: Session, user_id: str, exclude_user_id: UUID = None) -> bool:
    """Check if user_id already exists, optionally excluding a specific user."""
    query = db.query(User).filter(User.user_id == user_id)
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    return query.first() is not None


def update_user(db: Session, user: User, **kwargs):
    """Update user fields."""
    for key, value in kwargs.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
