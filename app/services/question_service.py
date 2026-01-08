# app/services/question_service.py
from sqlalchemy.orm import Session
from app.repository import question_repo


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


def get_questions_by_category_and_set_id(
    db: Session,
    category_id: str,
    question_set_id: str,
    search_key: str = None,
    search_value: str = None,
    page: int = 1,
    page_size: int = 10,
):
    """Get all questions for a specific category and question set with optional filtering and pagination."""
    return question_repo.get_questions_by_category_and_set_id(
        db, category_id, question_set_id, search_key, search_value, page, page_size
    )


def get_answers_by_question_id(
    db: Session,
    question_id: str,
    search_key: str = None,
    search_value: str = None,
    page: int = 1,
    page_size: int = 10,
):
    """Get all answers for a specific question with optional filtering and pagination."""
    return question_repo.get_answers_by_question_id(
        db, question_id, search_key, search_value, page, page_size
    )


def get_answer_by_id(db: Session, question_id: str, answer_id: str):
    """Get a specific answer by question_id and answer_id."""
    return question_repo.get_answer_by_id(db, question_id, answer_id)


def get_all_answers(
    db: Session,
    search_key: str = None,
    search_value: str = None,
    page: int = 1,
    page_size: int = 10,
):
    """Get all answers with optional filtering and pagination."""
    return question_repo.get_all_answers(
        db, search_key, search_value, page, page_size
    )


def get_answer_by_id_only(db: Session, answer_id: str):
    """Get a specific answer by answer_id only."""
    return question_repo.get_answer_by_id_only(db, answer_id)
