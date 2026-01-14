# app/repository/user_repo.py
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, Tuple, Dict, Any
from datetime import date
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
    query = db.query(User).order_by(User.created_at.desc())

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
        "role_id": {
            "column": User.role_id,
            "type": "exact",
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


def create_user(
    db: Session,
    email: str,
    full_name: str,
    hashed_password: str,
    user_id: str = None,
    role_id: UUID = None,
    phone: str = None,
    birthday: date = None,
    address: str = None,
    job_title: str = None,
    company: str = None,
    join_date: date = None,
) -> User:
    """Create a new user."""
    from app.utils.user_id_generator import generate_unique_user_id
    from app.repository.role_repo import get_default_role

    # Generate user_id if not provided
    if not user_id:
        user_id = generate_unique_user_id(db)

    # Get default role if role_id is not provided
    if not role_id:
        default_role = get_default_role(db)
        if default_role:
            role_id = default_role.id

    user = User(
        user_id=user_id,
        email=email,
        full_name=full_name,
        password=hashed_password,
        role_id=role_id,
        phone=phone,
        birthday=birthday,
        address=address,
        job_title=job_title,
        company=company,
        join_date=join_date,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, **kwargs):
    """Update user fields."""
    for key, value in kwargs.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: UUID) -> bool:
    """
    Soft delete a user.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        bool: True if deleted, False if not found
    """
    from datetime import datetime, timezone

    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()

    if not user:
        return False

    user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
