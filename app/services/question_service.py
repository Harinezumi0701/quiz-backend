# app/services/question_service.py
from sqlalchemy.orm import Session
from app.repository import question_repo


def get_categories_with_counts(db: Session):
    """Get all categories with their question counts."""
    categories = question_repo.get_all_categories(db)

    result = []
    for category in categories:
        count = question_repo.count_questions_by_category(db, category)
        result.append({
            'category': category,
            'question_count': count
        })

    return result


def get_categories_with_sets(db: Session):
    """Get all categories with their question sets/dumps."""
    categories = question_repo.get_all_categories(db)

    result = []
    for category in categories:
        # Get all question sets for this category
        sets_info = question_repo.get_question_sets_by_category(db, category)

        total_questions = sum(s['question_count'] for s in sets_info)

        result.append({
            'category': category,
            'total_questions': total_questions,
            'question_sets': sets_info
        })

    return result


def get_questions_by_category(db: Session, category: str):
    """Get all questions with answers for a specific category."""
    return question_repo.get_questions_by_category(db, category)


def get_questions_by_category_and_set(db: Session, category: str, question_set: str):
    """Get all questions with answers for a specific category and question set."""
    return question_repo.get_questions_by_category_and_set(db, category, question_set)


def get_all_questions(
    db: Session,
    search_key: str = None,
    search_value: str = None,
    page: int = 1,
    page_size: int = 10
):
    """Get all questions with optional filtering and pagination."""
    return question_repo.get_all_questions(db, search_key, search_value, page, page_size)


def get_question_by_id(db: Session, question_id: str):
    """Get a specific question by ID."""
    return question_repo.get_question_by_id(db, question_id)
