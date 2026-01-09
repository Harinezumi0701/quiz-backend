# app/api/v1/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.user import UserOut, UserListResponse, UserResponse
from app.schemas.http_response import ErrorResponse
from app.services import user_service
from app.db.session import get_db
from app.constants import ERROR_USER_NOT_FOUND

router = APIRouter()


@router.get(
    "",
    response_model=UserListResponse,
    summary="Get all users",
    description="Get list of all users in the system (public endpoint)",
    responses={
        200: {
            "description": "List of users",
        }
    }
)
def read_users(db: Session = Depends(get_db)):
    """
    Get list of all users.
    
    This endpoint does not require authentication.
    """
    users = user_service.list_users(db)
    return UserListResponse(data=users, meta={})


@router.get(
    "/{user_identifier}",
    response_model=UserResponse,
    summary="Get user information by ID or user_id",
    description="Get detailed information of a user by UUID ID or user_id (editable identifier) (public endpoint)",
    responses={
        200: {
            "description": "User information",
        },
        404: {
            "description": "User not found",
            "model": ErrorResponse,
        }
    }
)
def read_user(user_identifier: str, db: Session = Depends(get_db)):
    """
    Get user information by UUID ID or user_id (editable identifier).
    
    - **user_identifier**: UUID ID or user_id (6-character string) of the user to get information for
    
    This endpoint does not require authentication.
    """
    # Try to parse as UUID first
    try:
        user_uuid = UUID(user_identifier)
        user = user_service.get_user(db, user_uuid)
    except ValueError:
        # If not a valid UUID, try as user_id (editable identifier)
        user = user_service.get_user_by_user_id(db, user_identifier)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_FOUND)
    return UserResponse(data=user, meta={})
