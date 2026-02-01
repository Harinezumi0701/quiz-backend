# app/api/v1/me.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse, UserUpdateRequest, ChangePasswordRequest
from app.schemas.submission import DashboardResponse, SubmissionHistoryGroupedByTestResponse
from app.schemas.http_response import ErrorResponse
from app.services import submission_service, user_service, permission_service
from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.users import User

router = APIRouter()


@router.get(
    "",
    response_model=UserResponse,
    summary="Get current user information",
    description="Get information of the currently logged in user (requires authentication)",
    responses={
        200: {
            "description": "User information",
        },
        401: {
            "description": "Unauthorized access",
            "model": ErrorResponse,
        }
    }
)
def read_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user information including role and permissions.
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    # Get user permissions
    permissions = permission_service.get_user_permissions(db, current_user)
    
    # Create user data with role and permissions
    user_data = {
        "id": current_user.id,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "birthday": current_user.birthday,
        "address": current_user.address,
        "job_title": current_user.job_title,
        "company": current_user.company,
        "join_date": current_user.join_date,
        "permissions": permissions,
    }
    
    return UserResponse(data=user_data, meta={})


@router.put(
    "",
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update information of the currently logged in user (requires authentication)",
    responses={
        200: {
            "description": "User information updated",
        },
        400: {
            "description": "Invalid input or user_id already exists",
            "model": ErrorResponse,
        },
        401: {
            "description": "Unauthorized access",
            "model": ErrorResponse,
        }
    }
)
def update_current_user(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile information.
    
    - **user_id**: Editable unique identifier (1-125 characters matching [A-Za-z\\._-])
    - **full_name**: Full name
    - **phone**: Phone number
    - **birthday**: Birthday (YYYY-MM-DD)
    - **address**: Address
    - **job_title**: Job title
    - **company**: Company name
    - **join_date**: Join date (YYYY-MM-DD)
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    update_dict = update_data.model_dump(exclude_unset=True)
    updated_user = user_service.update_user_profile(db, current_user.id, update_dict)
    
    # Get user permissions
    permissions = permission_service.get_user_permissions(db, updated_user)
    
    # Create user data with role and permissions
    user_data = {
        "id": updated_user.id,
        "user_id": updated_user.user_id,
        "email": updated_user.email,
        "full_name": updated_user.full_name,
        "phone": updated_user.phone,
        "birthday": updated_user.birthday,
        "address": updated_user.address,
        "job_title": updated_user.job_title,
        "company": updated_user.company,
        "join_date": updated_user.join_date,
        "role_id": updated_user.role_id,
        "permissions": permissions,
    }
    
    return UserResponse(data=user_data, meta={})


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get dashboard data",
    description="Get user statistics (requires authentication)",
    responses={
        200: {
            "description": "Dashboard data",
        },
        401: {
            "description": "Unauthorized access",
            "model": ErrorResponse,
        }
    }
)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user dashboard data including overall statistics, by category and by test.

    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    dashboard_data = submission_service.get_user_dashboard_data(db, current_user.id)
    return DashboardResponse(data=dashboard_data, meta={})


@router.get(
    "/submission-history",
    response_model=SubmissionHistoryGroupedByTestResponse,
    summary="Get submission history grouped by test",
    description="Get all submission history of the current user grouped by test_id (requires authentication)",
    responses={
        200: {"description": "Submission history grouped by test"},
        401: {"description": "Unauthorized access", "model": ErrorResponse},
    },
)
def get_submission_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all submission history of the current user grouped by test_id."""
    data = submission_service.get_user_submission_history_grouped_by_test(db, current_user.id)
    return SubmissionHistoryGroupedByTestResponse(data=data, meta={})


@router.put(
    "/password",
    status_code=status.HTTP_200_OK,
    summary="Change user password",
    description="Change password for the currently logged in user (requires authentication)",
    responses={
        200: {
            "description": "Password changed successfully",
        },
        400: {
            "description": "Incorrect old password or new password same as old",
            "model": ErrorResponse,
        },
        401: {
            "description": "Unauthorized access",
            "model": ErrorResponse,
        }
    }
)
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    - **old_password**: Current password
    - **new_password**: New password (minimum 6 characters)
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    user_service.change_password(
        db=db,
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    return {"message": "Password changed successfully"}
