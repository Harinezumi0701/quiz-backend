# app/services/submission_service.py
from sqlalchemy.orm import Session
from typing import List
from app.repository import submission_repo
from app.schemas.submission import SubmissionCreate
from app.models.submissions import Submission


def submit_submission(db: Session, user_id: int, submission_data: SubmissionCreate) -> Submission:
    """Submit a single quiz submission."""
    return submission_repo.create_submission(db, user_id, submission_data)


def submit_submissions_bulk(db: Session, user_id: int, submissions: List[SubmissionCreate]) -> List[Submission]:
    """Submit multiple quiz submissions at once."""
    return submission_repo.create_submissions_bulk(db, user_id, submissions)


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

