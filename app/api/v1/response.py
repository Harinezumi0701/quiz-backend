# app/api/v1/response.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.response import DashboardData, ResponseCreate, ResponseBulkCreate, ResponseOut
from app.services import response_service
from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.users import User

router = APIRouter()


@router.post(
    "/submit",
    response_model=ResponseOut,
    summary="Submit a response",
    description="Submit a response for a question (requires authentication)",
    responses={
        200: {
            "description": "Response saved successfully",
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
def submit_response(
    response_data: ResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a response for a question.
    
    - **question_id**: Question ID
    - **selected_option_id**: Selected answer option ID
    - **is_correct**: Whether the answer is correct
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    return response_service.submit_response(db, current_user.id, response_data)


@router.post(
    "/submit-bulk",
    response_model=List[ResponseOut],
    summary="Submit multiple responses at once",
    description="Submit multiple responses in one request (requires authentication)",
    responses={
        200: {
            "description": "List of saved responses",
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
def submit_responses_bulk(
    bulk_data: ResponseBulkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit multiple responses at once.
    
    - **responses**: List of responses (minimum 1 response)
    
    Each response in the list includes:
    - question_id: Question ID
    - selected_option_id: Selected answer option ID
    - is_correct: Whether the answer is correct
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    return response_service.submit_responses_bulk(db, current_user.id, bulk_data.responses)


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
                            "total_correct": 120,
                            "total_wrong": 30,
                            "overall_accuracy": 0.8
                        },
                        "by_category": [
                            {
                                "category": "DVA-C02",
                                "total_answered": 50,
                                "correct_answers": 40,
                                "wrong_answers": 10,
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
    
    - **overall**: Overall statistics (total answered, correct, wrong, accuracy rate)
    - **by_category**: Statistics by category
    - **recent_activity**: Recent activity (most recently answered questions)
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    return response_service.get_user_dashboard_data(db, current_user.id)
