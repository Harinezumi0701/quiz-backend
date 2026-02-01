# app/services/submission_service.py
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from app.repository import submission_repo, question_repo, answer_repo
from app.schemas.submission import SubmissionCreate
from app.utils.datetime_utils import datetime_to_timestamp


def submit_submission(db: Session, user_id: UUID, submission_data: SubmissionCreate) -> dict:
    """Submit a single quiz submission."""
    # Validate submission before creating
    # Check if question exists
    if not question_repo.question_exists(db, submission_data.question_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {submission_data.question_id} not found"
        )
    
    # Check if answer exists for the question
    if not answer_repo.answer_exists_for_question(
        db, submission_data.question_id, submission_data.answer_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {submission_data.answer_id} not found for question {submission_data.question_id}"
        )
    
    submission = submission_repo.create_submission(db, user_id, submission_data)
    ts = datetime_to_timestamp(submission.answered_at)
    return {
        "id": submission.id,
        "user_id": submission.user_id,
        "question_id": submission.question_id,
        "answer_id": submission.answer_id,
        "is_correct": submission.is_correct,
        "answered_at": ts,
        "created_at": ts,
    }


def submit_submissions_bulk(db: Session, user_id: UUID, submissions: List[SubmissionCreate]) -> List[dict]:
    """Submit multiple quiz submissions at once."""
    # Validate all submissions before creating
    for submission in submissions:
        # Check if question exists
        if not question_repo.question_exists(db, submission.question_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {submission.question_id} not found"
            )
        
        # Check if answer exists for the question
        if not answer_repo.answer_exists_for_question(
            db, submission.question_id, submission.answer_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer with ID {submission.answer_id} not found for question {submission.question_id}"
            )
    
    db_submissions = submission_repo.create_submissions_bulk(db, user_id, submissions)
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "question_id": s.question_id,
            "answer_id": s.answer_id,
            "is_correct": s.is_correct,
            "answered_at": datetime_to_timestamp(s.answered_at),
            "created_at": datetime_to_timestamp(s.answered_at),
        }
        for s in db_submissions
    ]


def get_submissions_by_test_id(
    db: Session,
    test_id: str,
    page: int = 1,
    page_size: int = 10,
    request_params: Dict[str, Any] | None = None,
) -> Tuple[List[dict], int]:
    """Get submissions for a test with pagination and optional search filters."""
    return submission_repo.get_submissions_by_test_id(
        db, test_id, page=page, page_size=page_size, request_params=request_params
    )


def get_submission_history_by_id_for_test(
    db: Session, test_id: str, submission_history_id: str
) -> dict:
    """Get submission history by id for a test. Raises 404 if not found."""
    data = submission_repo.get_submission_history_by_id_for_test(
        db, test_id, submission_history_id
    )
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission history not found",
        )
    return data


def get_user_dashboard_data(db: Session, user_id: UUID):
    """Get comprehensive dashboard data for user."""
    statistics = submission_repo.get_user_statistics(db, user_id)
    statistics_by_test = submission_repo.get_user_statistics_by_test(db, user_id)
    total_submitted = sum(stat['total_submitted'] for stat in statistics)
    total_correct = sum(stat['correct_submissions'] for stat in statistics)
    return {
        'overall': {
            'total_answered': total_submitted,
            'total_submitted': total_submitted,
            'total_correct': total_correct,
            'total_wrong': total_submitted - total_correct,
            'overall_accuracy': round(total_correct / total_submitted * 100, 1) if total_submitted > 0 else 0
        },
        'by_category': statistics,
        'by_test': statistics_by_test,
    }


def get_user_submission_history_grouped_by_test(db: Session, user_id: UUID) -> List[dict]:
    """Get all submission history for a user grouped by test_id."""
    return submission_repo.get_user_submission_history_grouped_by_test(db, user_id)

