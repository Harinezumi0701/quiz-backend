# app/services/category_service.py
from sqlalchemy.orm import Session
from typing import Tuple, Dict, Any, Optional
from app.repository import category_repo, test_repo


def get_all_categories_with_search(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """Get all categories with optional name search and pagination."""
    return category_repo.get_all_categories_with_search(
        db, page=page, page_size=page_size, request_params=request_params
    )


def get_category_by_id(db: Session, category_id: str):
    """Get a specific category by ID."""
    return category_repo.get_category_by_id(db, category_id)


def get_tests_by_category_id(
    db: Session,
    category_id: str,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """Get all tests for a specific category with optional filtering and pagination."""
    return test_repo.get_tests_by_category_id(
        db, category_id, page=page, page_size=page_size, request_params=request_params
    )


def get_test_by_id(db: Session, category_id: str, test_id: str):
    """Get a specific test by category_id and test_id."""
    return test_repo.get_test_by_id(db, category_id, test_id)


def get_all_tests(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """Get all tests with optional filtering and pagination."""
    return test_repo.get_all_tests(
        db, page=page, page_size=page_size, request_params=request_params
    )


def get_test_by_id_only(db: Session, test_id: str):
    """Get a specific test by test_id only."""
    return test_repo.get_test_by_id_only(db, test_id)


def create_category(db: Session, name: str):
    """Create a new category."""
    return category_repo.create_category(db, name)


def update_category(db: Session, category_id: str, name: str):
    """Update a category."""
    return category_repo.update_category(db, category_id, name)


def delete_category(db: Session, category_id: str):
    """Delete a category (soft delete)."""
    return category_repo.delete_category(db, category_id)


def create_test(
    db: Session,
    name: str,
    category_id: str,
    time_limit: int,
    description: str | None = None,
):
    """Create a new test."""
    return test_repo.create_test(db, name, category_id, time_limit, description)


def update_test(
    db: Session,
    test_id: str,
    name: str,
    time_limit: int,
    description: str | None = None,
):
    """Update a test."""
    return test_repo.update_test(db, test_id, name, time_limit, description)


def delete_test(db: Session, test_id: str):
    """Delete a test (soft delete)."""
    return test_repo.delete_test(db, test_id)
