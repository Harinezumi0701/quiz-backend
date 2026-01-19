# app/repository/answer_repo.py
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional, Tuple, Dict, Any
from app.models.answer_options import AnswerOption
from app.models.questions import Question
from app.utils.search_pagination import paginate_query_with_multiple_filters
from app.utils.datetime_utils import datetime_to_timestamp


def get_answers_by_question_id(
    db: Session,
    question_id: str,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all answers for a specific question with optional filtering and pagination.

    Args:
        db: Database session
        question_id: Question UUID
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for multiple filters

    Returns:
        Tuple of (answers list, total count)
    """
    # Verify question exists
    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.deleted_at.is_(None))
        .first()
    )

    if not question:
        return [], 0

    # Base query
    query = db.query(AnswerOption).filter(
        AnswerOption.question_id == question_id, AnswerOption.deleted_at.is_(None)
    ).order_by(AnswerOption.created_at.desc())

    # Define search configuration
    # Define search configuration
    search_config = {
        "content": {
            "column": AnswerOption.content,
            "type": "text",
            "case_sensitive": False,
        },
        "is_correct": {
            "column": AnswerOption.is_correct,
            "type": "boolean",
        },
    }

    # Apply search filter and pagination
    paginated_query, total = paginate_query_with_multiple_filters(
        query,
        request_params=request_params or {},
        search_config=search_config,
        page=page,
        page_size=page_size,
    )

    # Execute query
    answers = paginated_query.all()

    result = []
    for answer in answers:
        result.append(
            {
                "id": answer.id,
                "question_id": answer.question_id,
                "content": answer.content,
                "image_url": answer.image_url,
                "is_correct": answer.is_correct,
                "explanation": answer.explanation,
                "created_at": datetime_to_timestamp(answer.created_at),
                "updated_at": datetime_to_timestamp(answer.updated_at),
            }
        )

    return result, total


def get_answer_by_id(
    db: Session,
    question_id: str,
    answer_id: str,
):
    """
    Get a specific answer by question_id and answer_id.

    Args:
        db: Database session
        question_id: Question UUID
        answer_id: Answer UUID

    Returns:
        Answer dict or None if not found
    """
    # Verify question exists
    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.deleted_at.is_(None))
        .first()
    )

    if not question:
        return None

    # Get answer
    answer = (
        db.query(AnswerOption)
        .filter(
            AnswerOption.id == answer_id,
            AnswerOption.question_id == question_id,
            AnswerOption.deleted_at.is_(None),
        )
        .first()
    )

    if not answer:
        return None

    return {
        "id": answer.id,
        "question_id": answer.question_id,
        "content": answer.content,
        "image_url": answer.image_url,
        "is_correct": answer.is_correct,
        "explanation": answer.explanation,
        "created_at": datetime_to_timestamp(answer.created_at),
        "updated_at": datetime_to_timestamp(answer.updated_at),
    }


def get_all_answers(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all answers with optional filtering and pagination.

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for multiple filters

    Returns:
        Tuple of (answers list, total count)
    """
    # Base query
    query = db.query(AnswerOption).filter(AnswerOption.deleted_at.is_(None)).order_by(AnswerOption.created_at.desc())

    # Define search configuration
    # Define search configuration
    search_config = {
        "content": {
            "column": AnswerOption.content,
            "type": "text",
            "case_sensitive": False,
        },
        "is_correct": {
            "column": AnswerOption.is_correct,
            "type": "boolean",
        },
        "question_id": {
            "column": AnswerOption.question_id,
            "type": "exact",
        },
    }

    # Apply search filter and pagination
    paginated_query, total = paginate_query_with_multiple_filters(
        query,
        request_params=request_params or {},
        search_config=search_config,
        page=page,
        page_size=page_size,
    )

    # Execute query
    answers = paginated_query.all()

    result = []
    for answer in answers:
        result.append(
            {
                "id": answer.id,
                "question_id": answer.question_id,
                "content": answer.content,
                "image_url": answer.image_url,
                "is_correct": answer.is_correct,
                "explanation": answer.explanation,
                "created_at": datetime_to_timestamp(answer.created_at),
                "updated_at": datetime_to_timestamp(answer.updated_at),
            }
        )

    return result, total


def get_answer_by_id_only(
    db: Session,
    answer_id: str,
):
    """
    Get a specific answer by answer_id only.

    Args:
        db: Database session
        answer_id: Answer UUID

    Returns:
        Answer dict or None if not found
    """
    # Get answer
    answer = (
        db.query(AnswerOption)
        .filter(AnswerOption.id == answer_id, AnswerOption.deleted_at.is_(None))
        .first()
    )

    if not answer:
        return None

    return {
        "id": answer.id,
        "question_id": answer.question_id,
        "content": answer.content,
        "image_url": answer.image_url,
        "is_correct": answer.is_correct,
        "explanation": answer.explanation,
        "created_at": datetime_to_timestamp(answer.created_at),
        "updated_at": datetime_to_timestamp(answer.updated_at),
    }


def answer_exists_for_question(db: Session, question_id: UUID, answer_id: UUID) -> bool:
    """
    Check if an answer exists for a specific question and is not deleted.

    Args:
        db: Database session
        question_id: Question UUID
        answer_id: Answer UUID

    Returns:
        True if answer exists for the question, False otherwise
    """
    answer = (
        db.query(AnswerOption)
        .filter(
            AnswerOption.id == answer_id,
            AnswerOption.question_id == question_id,
            AnswerOption.deleted_at.is_(None),
        )
        .first()
    )
    return answer is not None


def create_answer(
    db: Session,
    question_id: str,
    content: Optional[str] = None,
    image_url: Optional[str] = None,
    is_correct: bool = False,
    explanation: Optional[str] = None,
):
    """
    Create a new answer.

    Args:
        db: Database session
        question_id: Question UUID
        content: Optional answer content
        image_url: Optional image URL
        is_correct: Whether this is the correct answer
        explanation: Optional explanation

    Returns:
        Answer dict or None if question not found
    """
    # Verify question exists
    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.deleted_at.is_(None))
        .first()
    )
    if not question:
        return None

    answer = AnswerOption(
        question_id=question_id,
        content=content,
        image_url=image_url,
        is_correct=is_correct,
        explanation=explanation,
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    return {
        "id": answer.id,
        "question_id": answer.question_id,
        "content": answer.content,
        "image_url": answer.image_url,
        "is_correct": answer.is_correct,
        "explanation": answer.explanation,
        "created_at": datetime_to_timestamp(answer.created_at),
        "updated_at": datetime_to_timestamp(answer.updated_at),
    }


def update_answer(
    db: Session,
    answer_id: str,
    content: Optional[str] = None,
    image_url: Optional[str] = None,
    is_correct: Optional[bool] = None,
    explanation: Optional[str] = None,
):
    """
    Update an answer.

    Args:
        db: Database session
        answer_id: Answer UUID
        content: Optional new answer content
        image_url: Optional new image URL
        is_correct: Optional new is_correct value
        explanation: Optional new explanation

    Returns:
        Answer dict or None if not found
    """
    answer = (
        db.query(AnswerOption)
        .filter(AnswerOption.id == answer_id, AnswerOption.deleted_at.is_(None))
        .first()
    )

    if not answer:
        return None

    # Update fields if provided
    if content is not None:
        answer.content = content
    if image_url is not None:
        answer.image_url = image_url
    if is_correct is not None:
        answer.is_correct = is_correct
    if explanation is not None:
        answer.explanation = explanation

    db.commit()
    db.refresh(answer)

    return {
        "id": answer.id,
        "question_id": answer.question_id,
        "content": answer.content,
        "image_url": answer.image_url,
        "is_correct": answer.is_correct,
        "explanation": answer.explanation,
        "created_at": datetime_to_timestamp(answer.created_at),
        "updated_at": datetime_to_timestamp(answer.updated_at),
    }


def delete_answer(db: Session, answer_id: str):
    """
    Soft delete an answer.

    Args:
        db: Database session
        answer_id: Answer UUID

    Returns:
        bool: True if deleted, False if not found
    """
    from datetime import datetime, timezone

    answer = (
        db.query(AnswerOption)
        .filter(AnswerOption.id == answer_id, AnswerOption.deleted_at.is_(None))
        .first()
    )

    if not answer:
        return False

    answer.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
