# app/api/v1/submission.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.submission import DashboardData, SubmissionCreate, SubmissionBulkCreate, SubmissionOut
from app.services import submission_service
from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.users import User

router = APIRouter()


@router.post(
    "/submit",
    response_model=SubmissionOut,
    summary="Submit a submission",
    description="Submit a submission for a question (requires authentication)",
    responses={
        200: {
            "description": "Submission saved successfully",
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
    return submission_service.submit_submission(db, current_user.id, submission_data)


@router.post(
    "/submit-bulk",
    response_model=List[SubmissionOut],
    summary="Submit multiple submissions at once",
    description="Submit multiple submissions in one request (requires authentication)",
    responses={
        200: {
            "description": "List of saved submissions",
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
    return submission_service.submit_submissions_bulk(db, current_user.id, bulk_data.submissions)


@router.get(
    "/dashboard",
    response_model=DashboardData,
    summary="Get dashboard data",
    description="Get user statistics and recent activity (requires authentication)",
    responses={
        200: {
            "description": "Dashboard data",
            "content": {
                "application/json": {
                    "example": {
                        "overall": {
                            "total_answered": 150,
                            "total_submitted": 150,
                            "total_correct": 120,
                            "total_wrong": 30,
                            "overall_accuracy": 0.8
                        },
                        "by_category": [
                            {
                                "category": "DVA-C02",
                                "total_answered": 50,
                                "total_submitted": 50,
                                "correct_answers": 40,
                                "correct_submissions": 40,
                                "wrong_answers": 10,
                                "wrong_submissions": 10,
                                "accuracy": 0.8,
                                "last_attempt": "2024-01-01"
                            }
                        ],
                        "recent_activity": [
                            {
                                "id": 1,
                                "category": "DVA-C02",
                                "question_preview": "What is AWS Lambda?",
                                "is_correct": True,
                                "answered_at": "2024-01-01T12:00:00"
                            }
                        ]
                    }
                }
            }
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
    return submission_service.get_user_dashboard_data(db, current_user.id)

