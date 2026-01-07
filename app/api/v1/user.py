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


@router.get(
    "/",
    response_model=list[UserOut],
    summary="Get all users",
    description="Get list of all users in the system (public endpoint)",
    responses={
        200: {
            "description": "List of users",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "account_name": "John Doe",
                            "user_email": "john@example.com"
                        }
                    ]
                }
            }
        }
    }
)
def read_users(db: Session = Depends(get_db)):
    """
    Get list of all users.
    
    This endpoint does not require authentication.
    """
    users = user_service.list_users(db)
    return users


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user information",
    description="Get information of the currently logged in user (requires authentication)",
    responses={
        200: {
            "description": "User information",
        },
        401: {
            "description": "Unauthorized access",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        }
    }
)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Get user information by ID",
    description="Get detailed information of a user by ID (public endpoint)",
    responses={
        200: {
            "description": "User information",
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user information by ID.
    
    - **user_id**: ID of the user to get information for
    
    This endpoint does not require authentication.
    """
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=HTTP_STATUS_NOT_FOUND, detail=ERROR_USER_NOT_FOUND)
    return user
