# app/services/submission_service.py
from sqlalchemy.orm import Session
from typing import List
from app.repository import submission_repo
from app.schemas.submission import SubmissionCreate
from app.utils.datetime_utils import datetime_to_timestamp


def submit_submission(db: Session, user_id: int, submission_data: SubmissionCreate) -> dict:
    """Submit a single quiz submission."""
    submission = submission_repo.create_submission(db, user_id, submission_data)
    return {
        "id": submission.id,
        "user_id": submission.user_id,
        "question_id": submission.question_id,
        "selected_option_id": submission.selected_option_id,
        "is_correct": submission.is_correct,
        "answered_at": datetime_to_timestamp(submission.answered_at),
    }


def submit_submissions_bulk(db: Session, user_id: int, submissions: List[SubmissionCreate]) -> List[dict]:
    """Submit multiple quiz submissions at once."""
    db_submissions = submission_repo.create_submissions_bulk(db, user_id, submissions)
    return [
        {
            "id": submission.id,
            "user_id": submission.user_id,
            "question_id": submission.question_id,
            "selected_option_id": submission.selected_option_id,
            "is_correct": submission.is_correct,
            "answered_at": datetime_to_timestamp(submission.answered_at),
        }
        for submission in db_submissions
    ]


def get_user_dashboard_data(db: Session, user_id: int):
    """Get comprehensive dashboard data for user."""
    statistics = submission_repo.get_user_statistics(db, user_id)
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
        'recent_activity': recent_activity
    }

