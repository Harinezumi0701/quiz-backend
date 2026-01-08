# app/services/category_service.py
from sqlalchemy.orm import Session
from typing import Tuple
from app.repository import category_repo


def get_all_categories_with_search(db: Session, search_key: str = None, search_value: str = None):
    """Get all categories with optional name search."""
    return category_repo.get_all_categories_with_search(db, search_key, search_value)


def get_category_by_id(db: Session, category_id: str):
    """Get a specific category by ID."""
    return category_repo.get_category_by_id(db, category_id)


def get_question_sets_by_category_id(
    db: Session,
    category_id: str,
    search_key: str = None,
    search_value: str = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """Get all question sets for a specific category with optional filtering and pagination."""
    return category_repo.get_question_sets_by_category_id(
        db, category_id, search_key, search_value, page, page_size
    )


def get_question_set_by_id(db: Session, category_id: str, question_set_id: str):
    """Get a specific question set by category_id and question_set_id."""
    return category_repo.get_question_set_by_id(db, category_id, question_set_id)


def get_all_question_sets(
    db: Session,
    search_key: str = None,
    search_value: str = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """Get all question sets with optional filtering and pagination."""
    return category_repo.get_all_question_sets(
        db, search_key, search_value, page, page_size
    )


def get_question_set_by_id_only(db: Session, question_set_id: str):
    """Get a specific question set by question_set_id only."""
    return category_repo.get_question_set_by_id_only(db, question_set_id)
