# app/api/v1/me.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserResponse
from app.schemas.submission import DashboardResponse
from app.schemas.http_response import ErrorResponse
from app.services import submission_service
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
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    return UserResponse(data=current_user, meta={})


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
