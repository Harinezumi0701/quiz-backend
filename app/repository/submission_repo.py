# app/repository/submission_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List, Tuple
from uuid import UUID
from app.models.submissions import Submission
from app.models.questions import Question
from app.models.categories import Category
from app.models.tests import Test
from app.models.submission_history import SubmissionHistory
from app.schemas.submission import SubmissionCreate
from app.utils.datetime_utils import datetime_to_timestamp
from app.utils.search_pagination import paginate_query_with_multiple_filters
from app.constants import UNCATEGORIZED_CATEGORY_NAME, UNCATEGORIZED_TEST_NAME_NAME


def get_submissions_by_test_id(
    db: Session,
    test_id: str,
    page: int = 1,
    page_size: int = 10,
    request_params: Dict[str, Any] | None = None,
) -> Tuple[List[dict], int]:
    """
    Get submissions for a test with pagination and optional filters.

    Args:
        db: Database session
        test_id: Test UUID
        page: Page number (1-indexed)
        page_size: Items per page
        request_params: Query params for search (user_id, is_correct, answered_at)

    Returns:
        Tuple of (list of submission dicts, total count)
    """
    query = (
        db.query(Submission)
        .join(Question, Submission.question_id == Question.id)
        .filter(
            Question.test_id == test_id,
            Question.deleted_at.is_(None),
        )
        .order_by(Submission.answered_at.desc())
    )
    search_config = {
        "user_id": {"column": Submission.user_id, "type": "exact"},
        "is_correct": {"column": Submission.is_correct, "type": "boolean"},
        "answered_at": {"column": Submission.answered_at, "type": "date"},
    }
    paginated_query, total = paginate_query_with_multiple_filters(
        query,
        request_params=request_params or {},
        search_config=search_config,
        page=page,
        page_size=page_size,
    )
    rows = paginated_query.all()
    result = [
        {
            "id": s.id,
            "user_id": s.user_id,
            "question_id": s.question_id,
            "answer_id": s.answer_id,
            "is_correct": s.is_correct,
            "answered_at": datetime_to_timestamp(s.answered_at),
            "created_at": datetime_to_timestamp(s.answered_at),
        }
        for s in rows
    ]
    return result, total


def get_submission_history_by_id_for_test(
    db: Session, test_id: str, submission_history_id: str
) -> dict | None:
    """Get submission history by id with all submissions for the given test."""
    history = (
        db.query(SubmissionHistory)
        .filter(SubmissionHistory.id == submission_history_id)
        .first()
    )
    if not history:
        return None
    rows = (
        db.query(Submission)
        .join(Question, Submission.question_id == Question.id)
        .filter(
            Submission.submission_history_id == submission_history_id,
            Question.test_id == test_id,
            Question.deleted_at.is_(None),
        )
        .order_by(Submission.answered_at.asc())
        .all()
    )
    submissions = [
        {
            "id": s.id,
            "user_id": s.user_id,
            "question_id": s.question_id,
            "answer_id": s.answer_id,
            "is_correct": s.is_correct,
            "answered_at": datetime_to_timestamp(s.answered_at),
            "created_at": datetime_to_timestamp(s.answered_at),
        }
        for s in rows
    ]
    return {
        "id": history.id,
        "user_id": history.user_id,
        "submitted_at": datetime_to_timestamp(history.submitted_at),
        "submission_count": history.submission_count,
        "created_at": datetime_to_timestamp(history.created_at),
        "updated_at": datetime_to_timestamp(history.updated_at),
        "submissions": submissions,
    }


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


def get_user_submission_history_grouped_by_test(db: Session, user_id: UUID) -> List[dict]:
    """Get all submissions for a user grouped by test_id then by submission_history."""
    rows = (
        db.query(Submission, Question.test_id, Test.name, SubmissionHistory.submitted_at)
        .join(Question, Submission.question_id == Question.id)
        .outerjoin(Test, Question.test_id == Test.id)
        .outerjoin(SubmissionHistory, Submission.submission_history_id == SubmissionHistory.id)
        .filter(
            Submission.user_id == user_id,
            Question.deleted_at.is_(None),
            (Test.deleted_at.is_(None) | (Test.id.is_(None))),
        )
        .order_by(SubmissionHistory.submitted_at.desc().nulls_last(), Submission.answered_at.desc())
        .all()
    )
    grouped: Dict[Any, dict] = {}
    for submission, test_id, test_name, submitted_at in rows:
        tid = str(test_id) if test_id else None
        if tid not in grouped:
            grouped[tid] = {
                "test_id": tid,
                "test_name": test_name or UNCATEGORIZED_TEST_NAME_NAME,
                "histories": {},
            }
        hist_id = str(submission.submission_history_id) if submission.submission_history_id else None
        if hist_id not in grouped[tid]["histories"]:
            grouped[tid]["histories"][hist_id] = {
                "submission_history_id": hist_id,
                "submitted_at": datetime_to_timestamp(submitted_at) if submitted_at else datetime_to_timestamp(submission.answered_at),
                "submissions": [],
            }
        grouped[tid]["histories"][hist_id]["submissions"].append({
            "id": submission.id,
            "user_id": submission.user_id,
            "question_id": submission.question_id,
            "answer_id": submission.answer_id,
            "is_correct": submission.is_correct,
            "answered_at": datetime_to_timestamp(submission.answered_at),
            "created_at": datetime_to_timestamp(submission.answered_at),
        })
    result = []
    for g in grouped.values():
        histories = list(g["histories"].values())
        histories.sort(key=lambda h: h["submitted_at"] or 0, reverse=True)
        g["histories"] = histories
        result.append(g)
    return result
