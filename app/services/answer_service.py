# app/services/answer_service.py
from typing import Any

from sqlalchemy.orm import Session

from app.repository import answer_repo


def get_answers_by_question_id(
    db: Session,
    question_id: str,
    page: int = 1,
    page_size: int = 10,
    request_params: dict[str, Any] | None = None,
):
    """Get all answers for a specific question with optional filtering and pagination."""
    return answer_repo.get_answers_by_question_id(
        db, question_id, page=page, page_size=page_size, request_params=request_params
    )


def get_answer_by_id(db: Session, question_id: str, answer_id: str):
    """Get a specific answer by question_id and answer_id."""
    return answer_repo.get_answer_by_id(db, question_id, answer_id)


def get_all_answers(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: dict[str, Any] | None = None,
):
    """Get all answers with optional filtering and pagination."""
    return answer_repo.get_all_answers(
        db, page=page, page_size=page_size, request_params=request_params
    )


def get_answer_by_id_only(db: Session, answer_id: str):
    """Get a specific answer by answer_id only."""
    return answer_repo.get_answer_by_id_only(db, answer_id)


def create_answer(
    db: Session,
    question_id: str,
    content: str | None = None,
    image_url: str | None = None,
    is_correct: bool = False,
    explanation: str | None = None,
):
    """Create a new answer."""
    return answer_repo.create_answer(
        db, question_id, content, image_url, is_correct, explanation
    )


def update_answer(
    db: Session,
    answer_id: str,
    content: str | None = None,
    image_url: str | None = None,
    is_correct: bool | None = None,
    explanation: str | None = None,
):
    """Update an answer."""
    return answer_repo.update_answer(
        db, answer_id, content, image_url, is_correct, explanation
    )


def delete_answer(db: Session, answer_id: str):
    """Delete an answer (soft delete)."""
    return answer_repo.delete_answer(db, answer_id)
