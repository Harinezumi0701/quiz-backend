# app/services/submission_service.py
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repository import answer_repo, question_repo, submission_repo
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
    return {
        "id": submission.id,
        "user_id": submission.user_id,
        "question_id": submission.question_id,
        "answer_id": submission.answer_id,
        "is_correct": submission.is_correct,
        "answered_at": datetime_to_timestamp(submission.answered_at),
    }


def submit_submissions_bulk(db: Session, user_id: UUID, submissions: list[SubmissionCreate]) -> list[dict]:
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
            "id": submission.id,
            "user_id": submission.user_id,
            "question_id": submission.question_id,
            "answer_id": submission.answer_id,
            "is_correct": submission.is_correct,
            "answered_at": datetime_to_timestamp(submission.answered_at),
        }
        for submission in db_submissions
    ]


def get_user_dashboard_data(db: Session, user_id: UUID):
    """Get comprehensive dashboard data for user."""
    statistics = submission_repo.get_user_statistics(db, user_id)
    statistics_by_test = submission_repo.get_user_statistics_by_test(db, user_id)
    recent_activity = submission_repo.get_user_recent_activity(db, user_id, limit=10)

    # Calculate overall statistics
    total_submitted = sum(stat['total_submitted'] for stat in statistics)
    total_correct = sum(stat['correct_submissions'] for stat in statistics)

    return {
        'overall': {
            'total_answered': total_submitted,  # Keep for backward compatibility
            'total_submitted': total_submitted,
            'total_correct': total_correct,
            'total_wrong': total_submitted - total_correct,
            'overall_accuracy': round(total_correct / total_submitted * 100, 1) if total_submitted > 0 else 0
        },
        'by_category': statistics,
        'by_test': statistics_by_test,
        'recent_activity': recent_activity
    }

