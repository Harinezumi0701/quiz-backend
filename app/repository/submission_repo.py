# app/repository/submission_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
from app.models.submissions import Submission
from app.models.questions import Question
from app.models.categories import Category
from app.models.tests import Test
from app.models.users import User
from app.models.submission_history import SubmissionHistory
from app.schemas.submission import SubmissionCreate
from app.utils.datetime_utils import datetime_to_timestamp
from app.constants import UNCATEGORIZED_CATEGORY_NAME, UNCATEGORIZED_TEST_NAME_NAME


def create_submission(
    db: Session, user_id: UUID, submission_data: SubmissionCreate
) -> Submission:
    """Create a single submission record with submission history tracking."""
    # Create a submission history for this single submission
    submission_history = SubmissionHistory(user_id=user_id, submission_count=1)
    db.add(submission_history)
    db.flush()  # Get submission_history.id without committing

    db_submission = Submission(
        user_id=user_id,
        question_id=submission_data.question_id,
        answer_id=submission_data.answer_id,
        is_correct=submission_data.is_correct,
        submission_history_id=submission_history.id
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission


def create_submissions_bulk(
    db: Session, user_id: UUID, submissions: List[SubmissionCreate]
) -> List[Submission]:
    """Create multiple submission records at once with submission history tracking."""
    # Create a single submission history for this bulk submission
    submission_history = SubmissionHistory(
        user_id=user_id, submission_count=len(submissions)
    )
    db.add(submission_history)
    db.flush()  # Get submission_history.id without committing

    db_submissions = [
        Submission(
            user_id=user_id,
            question_id=s.question_id,
            answer_id=s.answer_id,
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


def get_user_statistics(db: Session, user_id: UUID):
    """Get user's quiz statistics grouped by category."""
    from sqlalchemy import Integer, case, func as sql_func

    stats = (
        db.query(
            sql_func.coalesce(Category.name, UNCATEGORIZED_CATEGORY_NAME).label("category_name"),
            func.count(Submission.id).label("total_submitted"),
            func.sum(case((Submission.is_correct == True, 1), else_=0)).label(
                "correct_submissions"
            ),
            func.max(Submission.answered_at).label("last_attempt"),
        )
        .select_from(Submission)
        .join(Question, Submission.question_id == Question.id)
        .outerjoin(Category, Question.category_id == Category.id)
        .filter(
            Submission.user_id == user_id,
            Question.deleted_at.is_(None),
            (Category.deleted_at.is_(None) | (Category.id.is_(None)))
        )
        .group_by(sql_func.coalesce(Category.name, UNCATEGORIZED_CATEGORY_NAME))
        .all()
    )

    return [
        {
            "category": stat[0] or UNCATEGORIZED_CATEGORY_NAME,
            "total_answered": stat[1],  # Keep for backward compatibility
            "total_submitted": stat[1],
            "correct_answers": stat[2] or 0,  # Keep for backward compatibility
            "correct_submissions": stat[2] or 0,
            "wrong_answers": stat[1]
            - (stat[2] or 0),  # Keep for backward compatibility
            "wrong_submissions": stat[1] - (stat[2] or 0),
            "accuracy": round((stat[2] or 0) / stat[1] * 100, 1) if stat[1] > 0 else 0,
            "last_attempt": datetime_to_timestamp(stat[3]),
        }
        for stat in stats
    ]


def get_user_statistics_by_test(db: Session, user_id: UUID):
    """Get user's quiz statistics grouped by category and test."""
    from sqlalchemy import Integer, case, func as sql_func

    stats = (
        db.query(
            sql_func.coalesce(Category.name, UNCATEGORIZED_CATEGORY_NAME).label("category_name"),
            Test.id.label("test_id"),
            Test.name.label("test_name"),
            func.count(Submission.id).label("total_submitted"),
            func.sum(case((Submission.is_correct == True, 1), else_=0)).label(
                "correct_submissions"
            ),
            func.max(Submission.answered_at).label("last_attempt"),
        )
        .select_from(Submission)
        .join(Question, Submission.question_id == Question.id)
        .outerjoin(Category, Question.category_id == Category.id)
        .outerjoin(Test, Question.test_id == Test.id)
        .filter(
            Submission.user_id == user_id,
            Question.deleted_at.is_(None),
            (Category.deleted_at.is_(None) | (Category.id.is_(None))),
            (Test.deleted_at.is_(None) | (Test.id.is_(None)))
        )
        .group_by(
            sql_func.coalesce(Category.name, UNCATEGORIZED_CATEGORY_NAME),
            Test.id,
            Test.name
        )
        .all()
    )

    # Group by category
    result = {}
    for stat in stats:
        category_name = stat[0] or UNCATEGORIZED_CATEGORY_NAME
        test_id = stat[1]
        test_name = stat[2] or UNCATEGORIZED_TEST_NAME_NAME
        total_submitted = stat[3]
        correct_submissions = stat[4] or 0
        last_attempt = stat[5]

        if category_name not in result:
            result[category_name] = []

        result[category_name].append({
            "test_id": str(test_id) if test_id else None,
            "test_name": test_name,
            "total_answered": total_submitted,  # Keep for backward compatibility
            "total_submitted": total_submitted,
            "correct_answers": correct_submissions,  # Keep for backward compatibility
            "correct_submissions": correct_submissions,
            "wrong_answers": total_submitted - correct_submissions,  # Keep for backward compatibility
            "wrong_submissions": total_submitted - correct_submissions,
            "accuracy": round(correct_submissions / total_submitted * 100, 1) if total_submitted > 0 else 0,
            "last_attempt": datetime_to_timestamp(last_attempt),
        })

    return result


def get_user_submission_history(db: Session, user_id: UUID, page: int = 1, page_size: int = 10):
    """Get paginated submission history for a user with submission details."""
    offset = (page - 1) * page_size

    total = db.query(SubmissionHistory).filter(SubmissionHistory.user_id == user_id).count()

    history_records = (
        db.query(SubmissionHistory)
        .filter(SubmissionHistory.user_id == user_id)
        .order_by(SubmissionHistory.submitted_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    result = []
    for record in history_records:
        submissions_data = []
        correct_count = 0
        for sub in record.submissions:
            if sub.is_correct:
                correct_count += 1
            question = sub.question
            submissions_data.append({
                "id": sub.id,
                "question_id": sub.question_id,
                "answer_id": sub.answer_id,
                "is_correct": sub.is_correct,
                "answered_at": datetime_to_timestamp(sub.answered_at),
                "category": question.category.name if question and question.category else None,
                "test_name": question.test.name if question and question.test else None,
                "question_preview": question.content if question else None,
            })

        result.append({
            "id": record.id,
            "submitted_at": datetime_to_timestamp(record.submitted_at),
            "submission_count": record.submission_count,
            "correct_count": correct_count,
            "wrong_count": record.submission_count - correct_count,
            "submissions": submissions_data,
        })

    return result, total


def delete_user_submissions(db: Session, user_id: UUID) -> None:
    """Hard delete all submissions and submission_history records for a user."""
    db.query(Submission).filter(Submission.user_id == user_id).delete(synchronize_session=False)
    db.query(SubmissionHistory).filter(SubmissionHistory.user_id == user_id).delete(synchronize_session=False)


def get_user_recent_activity(db: Session, user_id: UUID, limit: int = 10):
    """Get user's recent quiz activity."""
    activities = (
        db.query(
            Submission.id,
            Category.name.label("category_name"),
            Test.name.label("test_name"),
            Question.content,
            Submission.is_correct,
            Submission.answered_at,
        )
        .join(Question, Submission.question_id == Question.id)
        .outerjoin(Category, Question.category_id == Category.id)
        .outerjoin(Test, Question.test_id == Test.id)
        .filter(
            Submission.user_id == user_id,
            Question.deleted_at.is_(None),
            (Category.deleted_at.is_(None) | (Category.id.is_(None))),
            (Test.deleted_at.is_(None) | (Test.id.is_(None)))
        )
        .order_by(Submission.answered_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": activity[0],
            "category": activity[1] or UNCATEGORIZED_CATEGORY_NAME,
            "test_name": activity[2] or UNCATEGORIZED_TEST_NAME_NAME,
            "question_preview": activity[3],
            "is_correct": activity[4],
            "answered_at": datetime_to_timestamp(activity[5]),
        }
        for activity in activities
    ]
