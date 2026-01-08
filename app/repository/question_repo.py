# app/repository/question_repo.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, Tuple
from app.models.questions import Question
from app.models.answer_options import AnswerOption
from app.models.categories import Category
from app.utils.search_pagination import paginate_query


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
    category = (
        db.query(Category)
        .filter(Category.name == category, Category.deleted_at.is_(None))
        .first()
    )

    if not category:
        return []

    # Get all questions in this category grouped by question_set
    results = (
        db.query(
            Question.question_set,
            func.count(Question.id).label("question_count"),
            func.min(Question.id).label("min_id"),
            func.max(Question.id).label("max_id"),
        )
        .filter(Question.category_id == category.id, Question.deleted_at.is_(None))
        .group_by(Question.question_set)
        .all()
    )

    sets_info = []
    for result in results:
        question_set = result.question_set or "Default"
        question_range = f"{result.min_id}-{result.max_id}"

        sets_info.append(
            {
                "question_set": question_set,
                "question_count": result.question_count,
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
        .options(joinedload(Question.category))
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
                "category": question.category.name if question.category else None,
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
    category = (
        db.query(Category)
        .filter(Category.name == category, Category.deleted_at.is_(None))
        .first()
    )

    if not category:
        return []

    # Handle "Default" as NULL/None in database
    if question_set == "Default":
        questions = (
            db.query(Question)
            .options(joinedload(Question.category))
            .filter(
                Question.category_id == category.id,
                Question.question_set.is_(None),
                Question.deleted_at.is_(None),
            )
            .all()
        )
    else:
        questions = (
            db.query(Question)
            .options(joinedload(Question.category))
            .filter(
                Question.category_id == category.id,
                Question.question_set == question_set,
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
                "category": question.category.name if question.category else None,
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
    query = db.query(Question).filter(Question.deleted_at.is_(None))

    # Define search configuration
    search_config = {
        "content": {
            "column": Question.content,
            "type": "text",
            "case_sensitive": False,
        },
        "created_at": {"column": Question.created_at, "type": "date"},
        "question_set": {
            "column": Question.question_set,
            "type": "null",
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
    questions = paginated_query.options(joinedload(Question.category)).all()

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
                "category": question.category.name if question.category else None,
                "question_set": question.question_set,
                "created_at": question.created_at,
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
        .options(joinedload(Question.category))
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
        "category": question.category.name if question.category else None,
        "question_set": question.question_set,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
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
