# app/services/user_service.py
from sqlalchemy.orm import Session
from uuid import UUID
import re
from fastapi import HTTPException, status
from app.repository import user_repo
from app.constants import (
    ERROR_USER_NOT_FOUND,
    ERROR_USER_ID_ALREADY_EXISTS,
    ERROR_INVALID_USER_ID_FORMAT,
)

def list_users(db: Session):
    return user_repo.get_all_users(db)

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
    pattern = r'^[A-Za-z\._-]+$'
    return bool(re.match(pattern, user_id))

def update_user_profile(db: Session, user_id: UUID, update_data: dict):
    """Update user profile information."""
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_USER_NOT_FOUND
        )
    
    # Validate and check user_id if provided
    if 'user_id' in update_data and update_data['user_id'] is not None:
        new_user_id = update_data['user_id']
        if not validate_user_id_format(new_user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_INVALID_USER_ID_FORMAT
            )
        if user_repo.user_id_exists(db, new_user_id, exclude_user_id=user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_USER_ID_ALREADY_EXISTS
            )
    
    return user_repo.update_user(db, user, **update_data)
