# app/api/v1/submission.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.submission import (
    DashboardData, SubmissionCreate, SubmissionBulkCreate, SubmissionOut,
    SubmissionResponse, SubmissionListResponse, DashboardResponse
)
from app.schemas.http_response import ErrorResponse
from app.services import submission_service
from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.users import User

router = APIRouter()


@router.post(
    "/submit",
    response_model=SubmissionResponse,
    summary="Submit a submission",
    description="Submit a submission for a question (requires authentication)",
    responses={
        200: {
            "description": "Submission saved successfully",
        },
        401: {
            "description": "Unauthorized access",
            "model": ErrorResponse,
        }
    }
)
def submit_submission(
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a submission for a question.
    
    - **question_id**: Question ID
    - **selected_option_id**: Selected answer option ID
    - **is_correct**: Whether the submission is correct
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    submission = submission_service.submit_submission(db, current_user.id, submission_data)
    return SubmissionResponse(data=submission, meta={})


@router.post(
    "/submit-bulk",
    response_model=SubmissionListResponse,
    summary="Submit multiple submissions at once",
    description="Submit multiple submissions in one request (requires authentication)",
    responses={
        200: {
            "description": "List of saved submissions",
        },
        401: {
            "description": "Unauthorized access",
            "model": ErrorResponse,
        }
    }
)
def submit_submissions_bulk(
    bulk_data: SubmissionBulkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit multiple submissions at once.
    
    - **submissions**: List of submissions (minimum 1 submission)
    
    Each submission in the list includes:
    - question_id: Question ID
    - selected_option_id: Selected answer option ID
    - is_correct: Whether the submission is correct
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    submissions = submission_service.submit_submissions_bulk(db, current_user.id, bulk_data.submissions)
    return SubmissionListResponse(data=submissions, meta={})


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

