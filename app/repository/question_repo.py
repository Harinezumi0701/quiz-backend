# app/repository/question_repo.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, Tuple
from app.models.questions import Question
from app.models.answer_options import AnswerOption
from app.models.categories import Category
from app.models.question_sets import QuestionSet
from app.utils.search_pagination import paginate_query
from app.utils.datetime_utils import datetime_to_timestamp


def get_all_categories(db: Session):
    """Get all unique categories from categories table."""
    categories = db.query(Category).filter(Category.deleted_at.is_(None)).all()

    return [cat.name for cat in categories]


def count_questions_by_category(db: Session, category: str):
    """Count total questions in a category."""
    category = (
        db.query(Category)
        .filter(Category.name == category, Category.deleted_at.is_(None))
        .first()
    )

    if not category:
        return 0

    return (
        db.query(Question)
        .filter(Question.category_id == category.id, Question.deleted_at.is_(None))
        .count()
    )


def get_question_sets_by_category(db: Session, category: str):
    """Get all question sets/dumps for a specific category with their details."""
    category_obj = (
        db.query(Category)
        .filter(Category.name == category, Category.deleted_at.is_(None))
        .first()
    )

    if not category_obj:
        return []

    # Get all question sets for this category
    question_sets = (
        db.query(QuestionSet)
        .filter(
            QuestionSet.category_id == category_obj.id,
            QuestionSet.deleted_at.is_(None)
        )
        .all()
    )

    sets_info = []
    for qs in question_sets:
        # Count questions in this set
        question_count = (
            db.query(Question)
            .filter(
                Question.question_set_id == qs.id,
                Question.deleted_at.is_(None)
            )
            .count()
        )

        # Get min and max question IDs for range
        result = (
            db.query(
                func.min(Question.id).label("min_id"),
                func.max(Question.id).label("max_id"),
            )
            .filter(
                Question.question_set_id == qs.id,
                Question.deleted_at.is_(None)
            )
            .first()
        )

        question_range = f"{result.min_id}-{result.max_id}" if result and result.min_id else "N/A"

        sets_info.append(
            {
                "question_set": qs.name,
                "question_count": question_count,
                "question_range": question_range,
            }
        )

    # Also include questions without question_set (Default)
    questions_without_set = (
        db.query(Question)
        .filter(
            Question.category_id == category_obj.id,
            Question.question_set_id.is_(None),
            Question.deleted_at.is_(None)
        )
        .count()
    )

    if questions_without_set > 0:
        result = (
            db.query(
                func.min(Question.id).label("min_id"),
                func.max(Question.id).label("max_id"),
            )
            .filter(
                Question.category_id == category_obj.id,
                Question.question_set_id.is_(None),
                Question.deleted_at.is_(None)
            )
            .first()
        )
        question_range = f"{result.min_id}-{result.max_id}" if result and result.min_id else "N/A"
        sets_info.append(
            {
                "question_set": "Default",
                "question_count": questions_without_set,
                "question_range": question_range,
            }
        )

    return sets_info


def get_questions_by_category(db: Session, category: str):
    """Get all questions with answers for a specific category."""
    category = (
        db.query(Category)
        .filter(Category.name == category, Category.deleted_at.is_(None))
        .first()
    )

    if not category:
        return []

    questions = (
        db.query(Question)
        .options(joinedload(Question.category_obj), joinedload(Question.question_set_obj))
        .filter(Question.category_id == category.id, Question.deleted_at.is_(None))
        .all()
    )

    result = []
    for question in questions:
        # Get all answer options for this question
        answers = (
            db.query(AnswerOption)
            .filter(
                AnswerOption.question_id == question.id,
                AnswerOption.deleted_at.is_(None),
            )
            .all()
        )

        result.append(
            {
                "id": question.id,
                "content": question.content,
                "image_url": question.image_url,
                "category": question.category_obj.name if question.category_obj else None,
                "question_set": question.question_set,
                "answers": [
                    {
                        "id": answer.id,
                        "content": answer.content,
                        "is_correct": answer.is_correct,
                        "explanation": answer.explanation,
                    }
                    for answer in answers
                ],
            }
        )

    return result


def get_questions_by_category_and_set(db: Session, category: str, question_set: str):
    """Get all questions with answers for a specific category and question set."""
    category_obj = (
        db.query(Category)
        .filter(Category.name == category, Category.deleted_at.is_(None))
        .first()
    )

    if not category_obj:
        return []

    # Handle "Default" as NULL/None in database
    if question_set == "Default":
        questions = (
            db.query(Question)
            .options(joinedload(Question.category_obj), joinedload(Question.question_set_obj))
            .filter(
                Question.category_id == category_obj.id,
                Question.question_set_id.is_(None),
                Question.deleted_at.is_(None),
            )
            .all()
        )
    else:
        # Find question_set by name and category
        question_set_obj = (
            db.query(QuestionSet)
            .filter(
                QuestionSet.name == question_set,
                QuestionSet.category_id == category_obj.id,
                QuestionSet.deleted_at.is_(None)
            )
            .first()
        )

        if not question_set_obj:
            return []

        questions = (
            db.query(Question)
            .options(joinedload(Question.category_obj), joinedload(Question.question_set_obj))
            .filter(
                Question.category_id == category_obj.id,
                Question.question_set_id == question_set_obj.id,
                Question.deleted_at.is_(None),
            )
            .all()
        )

    result = []
    for question in questions:
        # Get all answer options for this question
        answers = (
            db.query(AnswerOption)
            .filter(
                AnswerOption.question_id == question.id,
                AnswerOption.deleted_at.is_(None),
            )
            .all()
        )

        result.append(
            {
                "id": question.id,
                "content": question.content,
                "image_url": question.image_url,
                "category": question.category_obj.name if question.category_obj else None,
                "question_set": question.question_set,
                "answers": [
                    {
                        "id": answer.id,
                        "content": answer.content,
                        "is_correct": answer.is_correct,
                        "explanation": answer.explanation,
                    }
                    for answer in answers
                ],
            }
        )

    return result


def get_all_questions(
    db: Session,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """
    Get all questions with optional filtering and pagination.

    Args:
        db: Database session
        search_key: Field to search (content, created_at, question_set)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (questions list, total count)
    """
    # Always join with QuestionSet (left outer join) to enable question_set search
    query = (
        db.query(Question)
        .outerjoin(QuestionSet, Question.question_set_id == QuestionSet.id)
        .filter(Question.deleted_at.is_(None))
    )

    # Define search configuration
    search_config = {
        "content": {
            "column": Question.content,
            "type": "text",
            "case_sensitive": False,
        },
        "created_at": {"column": Question.created_at, "type": "date"},
        "question_set": {
            "column": QuestionSet.name,
            "type": "text",
            "case_sensitive": False,
        },
    }

    # Apply search filter and pagination using helper
    paginated_query, total = paginate_query(
        query,
        search_key=search_key,
        search_value=search_value,
        search_config=search_config,
        page=page,
        page_size=page_size,
    )

    # Apply eager loading and execute query
    questions = paginated_query.options(
        joinedload(Question.category_obj),
        joinedload(Question.question_set_obj)
    ).all()

    result = []
    for question in questions:
        # Get all answer options for this question
        answers = (
            db.query(AnswerOption)
            .filter(
                AnswerOption.question_id == question.id,
                AnswerOption.deleted_at.is_(None),
            )
            .all()
        )

        result.append(
            {
                "id": question.id,
                "content": question.content,
                "image_url": question.image_url,
                "category": question.category_obj.name if question.category_obj else None,
                "question_set": question.question_set,
                "created_at": datetime_to_timestamp(question.created_at),
                "answers": [
                    {
                        "id": answer.id,
                        "content": answer.content,
                        "is_correct": answer.is_correct,
                        "explanation": answer.explanation,
                    }
                    for answer in answers
                ],
            }
        )

    return result, total


def get_questions_by_category_and_set_id(
    db: Session,
    category_id: str,
    question_set_id: str,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """
    Get all questions for a specific category and question set with optional filtering and pagination.

    Args:
        db: Database session
        category_id: Category UUID
        question_set_id: Question set UUID
        search_key: Field to search (content, created_at)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (questions list, total count)
    """
    # Verify category exists
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        return [], 0

    # Verify question set exists and belongs to category
    question_set = db.query(QuestionSet).filter(
        QuestionSet.id == question_set_id,
        QuestionSet.category_id == category_id,
        QuestionSet.deleted_at.is_(None)
    ).first()

    if not question_set:
        return [], 0

    # Base query
    query = (
        db.query(Question)
        .filter(
            Question.category_id == category_id,
            Question.question_set_id == question_set_id,
            Question.deleted_at.is_(None)
        )
    )

    # Define search configuration
    search_config = {
        "content": {
            "column": Question.content,
            "type": "text",
            "case_sensitive": False,
        },
        "created_at": {"column": Question.created_at, "type": "date"},
    }

    # Apply search filter and pagination
    paginated_query, total = paginate_query(
        query,
        search_key=search_key,
        search_value=search_value,
        search_config=search_config,
        page=page,
        page_size=page_size,
    )

    # Apply eager loading and execute query
    questions = paginated_query.options(
        joinedload(Question.category_obj),
        joinedload(Question.question_set_obj)
    ).all()

    result = []
    for question in questions:
        # Get all answer options for this question
        answers = (
            db.query(AnswerOption)
            .filter(
                AnswerOption.question_id == question.id,
                AnswerOption.deleted_at.is_(None),
            )
            .all()
        )

        result.append(
            {
                "id": question.id,
                "content": question.content,
                "image_url": question.image_url,
                "category": question.category_obj.name if question.category_obj else None,
                "question_set": question.question_set,
                "created_at": datetime_to_timestamp(question.created_at),
                "answers": [
                    {
                        "id": answer.id,
                        "content": answer.content,
                        "is_correct": answer.is_correct,
                        "explanation": answer.explanation,
                    }
                    for answer in answers
                ],
            }
        )

    return result, total


def get_question_by_id(db: Session, question_id: str):
    """Get a specific question by ID with answers."""
    question = (
        db.query(Question)
        .options(joinedload(Question.category_obj))
        .filter(Question.id == question_id, Question.deleted_at.is_(None))
        .first()
    )

    if not question:
        return None

    # Get all answer options for this question
    answers = (
        db.query(AnswerOption)
        .filter(
            AnswerOption.question_id == question.id, AnswerOption.deleted_at.is_(None)
        )
        .all()
    )

    return {
        "id": question.id,
        "content": question.content,
        "image_url": question.image_url,
        "category": question.category_obj.name if question.category_obj else None,
        "question_set": question.question_set,
        "created_at": datetime_to_timestamp(question.created_at),
        "updated_at": datetime_to_timestamp(question.updated_at),
        "answers": [
            {
                "id": answer.id,
                "content": answer.content,
                "is_correct": answer.is_correct,
                "explanation": answer.explanation,
            }
            for answer in answers
        ],
    }
