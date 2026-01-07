# app/api/v1/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserOut
from app.services import user_service
from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.users import User
from app.constants import HTTP_STATUS_NOT_FOUND, ERROR_USER_NOT_FOUND

router = APIRouter()

@router.get("/", response_model=list[UserOut])
def read_users(db: Session = Depends(get_db)):
    """Get all users (public endpoint)."""
    users = user_service.list_users(db)
    return users

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Get current authenticated user (protected endpoint)."""
    return current_user

@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID (public endpoint)."""
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=HTTP_STATUS_NOT_FOUND, detail=ERROR_USER_NOT_FOUND)
    return user
