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


def get_tests_by_category_id(
    db: Session,
    category_id: str,
    search_key: str = None,
    search_value: str = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """Get all tests for a specific category with optional filtering and pagination."""
    return category_repo.get_tests_by_category_id(
        db, category_id, search_key, search_value, page, page_size
    )


def get_test_by_id(db: Session, category_id: str, test_id: str):
    """Get a specific test by category_id and test_id."""
    return category_repo.get_test_by_id(db, category_id, test_id)


def get_all_tests(
    db: Session,
    search_key: str = None,
    search_value: str = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """Get all tests with optional filtering and pagination."""
    return category_repo.get_all_tests(
        db, search_key, search_value, page, page_size
    )


def get_test_by_id_only(db: Session, test_id: str):
    """Get a specific test by test_id only."""
    return category_repo.get_test_by_id_only(db, test_id)


def create_category(db: Session, name: str):
    """Create a new category."""
    return category_repo.create_category(db, name)


def update_category(db: Session, category_id: str, name: str):
    """Update a category."""
    return category_repo.update_category(db, category_id, name)


def delete_category(db: Session, category_id: str):
    """Delete a category (soft delete)."""
    return category_repo.delete_category(db, category_id)
