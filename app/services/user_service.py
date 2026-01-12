# app/services/user_service.py
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Any, Optional, Tuple
import re
from fastapi import HTTPException, status
from app.repository import user_repo
from app.utils.security import verify_password, get_password_hash
from app.constants import (
    ERROR_USER_NOT_FOUND,
    ERROR_USER_ID_ALREADY_EXISTS,
    ERROR_INVALID_USER_ID_FORMAT,
    ERROR_INCORRECT_OLD_PASSWORD,
    ERROR_NEW_PASSWORD_SAME_AS_OLD,
)


def list_users(
    db: Session,
    search_key: str = None,
    search_value: str = None,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """Get all users with optional filtering and pagination."""
    return user_repo.get_all_users(
        db, search_key, search_value, page, page_size, request_params
    )


def get_user(db: Session, user_id: UUID):
    """Get user by UUID id."""
    return user_repo.get_user_by_id(db, user_id)


def get_user_by_user_id(db: Session, user_id: str):
    """Get user by user_id (editable unique identifier)."""
    return user_repo.get_user_by_user_id(db, user_id)


def validate_user_id_format(user_id: str) -> bool:
    """Validate user_id format matches [A-Za-z\\._-]{1,125}."""
    if not user_id or len(user_id) > 125:
        return False
    pattern = r"^[A-Za-z\._-]+$"
    return bool(re.match(pattern, user_id))


def update_user_profile(db: Session, user_id: UUID, update_data: dict):
    """Update user profile information."""
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_FOUND
        )

    # Validate and check user_id if provided
    if "user_id" in update_data and update_data["user_id"] is not None:
        new_user_id = update_data["user_id"]
        if not validate_user_id_format(new_user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_INVALID_USER_ID_FORMAT,
            )
        if user_repo.user_id_exists(db, new_user_id, exclude_user_id=user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_USER_ID_ALREADY_EXISTS,
            )

    return user_repo.update_user(db, user, **update_data)


def change_password(db: Session, user_id: UUID, old_password: str, new_password: str):
    """Change user password."""
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_FOUND
        )

    # Verify old password
    if not verify_password(old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_INCORRECT_OLD_PASSWORD
        )

    # Check if new password is different from old password
    if verify_password(new_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_NEW_PASSWORD_SAME_AS_OLD,
        )

    # Hash new password and update
    hashed_password = get_password_hash(new_password)
    return user_repo.update_user(db, user, password=hashed_password)
