# app/repository/submission_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.models.submissions import Submission
from app.models.questions import Question
from app.models.users import User
from app.models.submission_history import SubmissionHistory
from app.schemas.submission import SubmissionCreate


def create_submission(db: Session, user_id: int, submission_data: SubmissionCreate) -> Submission:
    """Create a single submission record with submission history tracking."""
    # Create a submission history for this single submission
    submission_history = SubmissionHistory(
        user_id=user_id,
        submission_count=1
    )
    db.add(submission_history)
    db.flush()  # Get submission_history.id without committing
    
    db_submission = Submission(
        user_id=user_id,
        question_id=submission_data.question_id,
        selected_option_id=submission_data.selected_option_id,
        is_correct=submission_data.is_correct,
        submission_history_id=submission_history.id
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission


def create_submissions_bulk(db: Session, user_id: int, submissions: List[SubmissionCreate]) -> List[Submission]:
    """Create multiple submission records at once with submission history tracking."""
    # Create a single submission history for this bulk submission
    submission_history = SubmissionHistory(
        user_id=user_id,
        submission_count=len(submissions)
    )
    db.add(submission_history)
    db.flush()  # Get submission_history.id without committing
    
    db_submissions = [
        Submission(
            user_id=user_id,
            question_id=s.question_id,
            selected_option_id=s.selected_option_id,
            is_correct=s.is_correct,
            submission_history_id=submission_history.id
        )
        for s in submissions
    ]
    db.add_all(db_submissions)
    db.commit()
    for s in db_submissions:
        db.refresh(s)
    return db_submissions


def get_user_statistics(db: Session, user_id: int):
    """Get user's quiz statistics grouped by category."""
    from sqlalchemy import Integer, case

    stats = db.query(
        Question.category,
        func.count(Submission.id).label('total_submitted'),
        func.sum(case((Submission.is_correct == True, 1), else_=0)).label('correct_submissions'),
        func.max(Submission.answered_at).label('last_attempt')
    ).join(
        Submission, Submission.question_id == Question.id
    ).filter(
        Submission.user_id == user_id,
        Question.deleted_at.is_(None)
    ).group_by(
        Question.category
    ).all()

    return [
        {
            'category': stat[0],
            'total_answered': stat[1],  # Keep for backward compatibility
            'total_submitted': stat[1],
            'correct_answers': stat[2] or 0,  # Keep for backward compatibility
            'correct_submissions': stat[2] or 0,
            'wrong_answers': stat[1] - (stat[2] or 0),  # Keep for backward compatibility
            'wrong_submissions': stat[1] - (stat[2] or 0),
            'accuracy': round((stat[2] or 0) / stat[1] * 100, 1) if stat[1] > 0 else 0,
            'last_attempt': stat[3].isoformat() if stat[3] else None
        }
        for stat in stats
    ]


def get_user_recent_activity(db: Session, user_id: int, limit: int = 10):
    """Get user's recent quiz activity."""
    activities = db.query(
        Submission.id,
        Question.category,
        Question.content,
        Submission.is_correct,
        Submission.answered_at
    ).join(
        Question, Submission.question_id == Question.id
    ).filter(
        Submission.user_id == user_id,
        Question.deleted_at.is_(None)
    ).order_by(
        Submission.answered_at.desc()
    ).limit(limit).all()

    return [
        {
            'id': activity[0],
            'category': activity[1],
            'question_preview': activity[2][:100] + '...' if len(activity[2]) > 100 else activity[2],
            'is_correct': activity[3],
            'answered_at': activity[4].isoformat() if activity[4] else None
        }
        for activity in activities
    ]

