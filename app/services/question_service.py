# app/services/question_service.py
from typing import Any

from sqlalchemy.orm import Session

from app.repository import question_repo


def get_all_questions(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: dict[str, Any] | None = None
):
    """Get all questions with optional filtering and pagination."""
    return question_repo.get_all_questions(db, page=page, page_size=page_size, request_params=request_params)


def get_question_by_id(db: Session, question_id: str):
    """Get a specific question by ID."""
    return question_repo.get_question_by_id(db, question_id)


def get_questions_by_category_and_test_id(
    db: Session,
    category_id: str,
    test_id: str,
    page: int = 1,
    page_size: int = 10,
    request_params: dict[str, Any] | None = None,
):
    """Get all questions for a specific category and test with optional filtering and pagination."""
    return question_repo.get_questions_by_category_and_test_id(
        db, category_id, test_id, page=page, page_size=page_size, request_params=request_params
    )


def get_questions_by_test_id(
    db: Session,
    test_id: str,
    page: int = 1,
    page_size: int = 10,
    request_params: dict[str, Any] | None = None,
):
    """Get all questions for a specific test with optional filtering and pagination."""
    return question_repo.get_questions_by_test_id(
        db, test_id, page=page, page_size=page_size, request_params=request_params
    )


def get_question_by_test_and_id(
    db: Session,
    test_id: str,
    question_id: str,
):
    """Get a specific question by test_id and question_id."""
    return question_repo.get_question_by_test_and_id(
        db, test_id, question_id
    )


def create_question(
    db: Session,
    content: str,
    image_url: str | None = None,
    category_id: str | None = None,
    test_id: str | None = None,
    is_multiple_choice: bool = False,
):
    """Create a new question."""
    return question_repo.create_question(
        db, content, image_url, category_id, test_id, is_multiple_choice
    )


def update_question(
    db: Session,
    question_id: str,
    content: str | None = None,
    image_url: str | None = None,
    category_id: str | None = None,
    test_id: str | None = None,
    is_multiple_choice: bool | None = None,
):
    """Update a question."""
    return question_repo.update_question(
        db, question_id, content, image_url, category_id, test_id, is_multiple_choice
    )


def delete_question(db: Session, question_id: str):
    """Delete a question (soft delete)."""
    return question_repo.delete_question(db, question_id)
