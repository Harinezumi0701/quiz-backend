# app/api/v1/me.py
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse, UserUpdateRequest, ChangePasswordRequest
from app.schemas.submission import DashboardResponse, SubmissionHistoryListResponse
from app.schemas.http_response import ErrorResponse
from app.services import submission_service, user_service, permission_service
from app.repository import submission_repo
from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.users import User
from app.utils.search_pagination import get_pagination_meta

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
        "role_id": current_user.role_id,
        "role_name": current_user.role_obj.name if current_user.role_obj else None,
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
        "role_name": updated_user.role_obj.name if updated_user.role_obj else None,
        "permissions": permissions,
    }
    
    return UserResponse(data=user_data, meta={})


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get dashboard data",
    description="Get user statistics and recent activity (requires authentication)",
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
    Get user dashboard data including:
    
    - **overall**: Overall statistics (total submitted, correct, wrong, accuracy rate)
    - **by_category**: Statistics by category
    - **recent_activity**: Recent activity (most recently submitted questions)
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    dashboard_data = submission_service.get_user_dashboard_data(db, current_user.id)
    return DashboardResponse(data=dashboard_data, meta={})


@router.get(
    "/submission-history",
    response_model=SubmissionHistoryListResponse,
    summary="Get current user submission history",
    description="Get paginated submission history for the currently logged in user (requires authentication)",
    responses={
        200: {"description": "Submission history"},
        401: {"description": "Unauthorized access", "model": ErrorResponse},
    },
)
def get_submission_history(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    search: str = Query(None, description="Search by test name"),
    sort_by: str = Query("submitted_at", description="Sort field: submitted_at | test_name | category"),
    sort_order: str = Query("desc", description="Sort order: asc | desc"),
    date_from: int = Query(None, description="Filter from date (Unix timestamp)"),
    date_to: int = Query(None, description="Filter to date (Unix timestamp)"),
    category: str = Query(None, description="Filter by category name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get submission history for the current user.

    Each record represents one submit action and contains the list of submitted answers.

    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    history, total = submission_repo.get_user_submission_history(
        db,
        current_user.id,
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        date_from=date_from,
        date_to=date_to,
        category=category,
    )
    meta = get_pagination_meta(total, page, page_size)
    return SubmissionHistoryListResponse(data=history, meta=meta)


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
