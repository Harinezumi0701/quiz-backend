# app/repository/question_repo.py
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from typing import Optional, Tuple, Dict, Any
from app.models.questions import Question
from app.models.answer_options import AnswerOption
from app.models.categories import Category
from app.models.tests import Test
from app.utils.search_pagination import (
    paginate_query,
    paginate_query_with_multiple_filters,
)
from app.utils.datetime_utils import datetime_to_timestamp


def get_all_questions(
    db: Session,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all questions with optional filtering and pagination.

    Args:
        db: Database session
        search_key: Field to search (content, created_at, test)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for multiple filters

    Returns:
        Tuple of (questions list, total count)
    """
    # Always join with Test (left outer join) to enable test search
    query = (
        db.query(Question)
        .outerjoin(Test, Question.test_id == Test.id)
        .filter(Question.deleted_at.is_(None))
        .order_by(Question.created_at.desc())
    )

    # Define search configuration
    search_config = {
        "content": {
            "column": Question.content,
            "type": "text",
            "case_sensitive": False,
        },
        "created_at": {"column": Question.created_at, "type": "date"},
        "test": {
            "column": Test.name,
            "type": "text",
            "case_sensitive": False,
        },
        "is_multiple_choice": {
            "column": Question.is_multiple_choice,
            "type": "boolean",
        },
        "category_id": {
            "column": Question.category_id,
            "type": "exact",
        },
        "test_id": {
            "column": Question.test_id,
            "type": "exact",
        },
    }

    # Apply search filter and pagination using helper
    if request_params:
        paginated_query, total = paginate_query_with_multiple_filters(
            query,
            request_params=request_params,
            search_config=search_config,
            page=page,
            page_size=page_size,
        )
    else:
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
        joinedload(Question.category_obj), joinedload(Question.test_obj)
    ).all()

    result = []
    for question in questions:
        result.append(
            {
                "id": question.id,
                "content": question.content,
                "image_url": question.image_url,
                "category": (
                    question.category_obj.name if question.category_obj else None
                ),
                "test": question.test,
                "is_multiple_choice": question.is_multiple_choice,
                "created_at": datetime_to_timestamp(question.created_at),
            }
        )

    return result, total


def get_questions_by_category_and_test_id(
    db: Session,
    category_id: str,
    test_id: str,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all questions for a specific category and test with optional filtering and pagination.

    Args:
        db: Database session
        category_id: Category UUID
        test_id: Test UUID
        search_key: Field to search (content, created_at)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for multiple filters

    Returns:
        Tuple of (questions list, total count)
    """
    # Verify category exists
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.deleted_at.is_(None))
        .first()
    )

    if not category:
        return [], 0

    # Verify test exists and belongs to category
    test = (
        db.query(Test)
        .filter(
            Test.id == test_id,
            Test.category_id == category_id,
            Test.deleted_at.is_(None),
        )
        .first()
    )

    if not test:
        return [], 0

    # Base query
    query = db.query(Question).filter(
        Question.category_id == category_id,
        Question.test_id == test_id,
        Question.deleted_at.is_(None),
    ).order_by(Question.created_at.desc())

    # Define search configuration
    search_config = {
        "content": {
            "column": Question.content,
            "type": "text",
            "case_sensitive": False,
        },
        "created_at": {"column": Question.created_at, "type": "date"},
        "is_multiple_choice": {
            "column": Question.is_multiple_choice,
            "type": "boolean",
        },
    }

    # Apply search filter and pagination
    if request_params:
        paginated_query, total = paginate_query_with_multiple_filters(
            query,
            request_params=request_params,
            search_config=search_config,
            page=page,
            page_size=page_size,
        )
    else:
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
        joinedload(Question.category_obj), joinedload(Question.test_obj)
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
                "category": (
                    question.category_obj.name if question.category_obj else None
                ),
                "test": question.test,
                "is_multiple_choice": question.is_multiple_choice,
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


def get_questions_by_test_id(
    db: Session,
    test_id: str,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all questions for a specific test with optional filtering and pagination.

    Args:
        db: Database session
        test_id: Test UUID
        search_key: Field to search (content, created_at)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for multiple filters

    Returns:
        Tuple of (questions list, total count)
    """
    # Verify test exists
    test = db.query(Test).filter(Test.id == test_id, Test.deleted_at.is_(None)).first()

    if not test:
        return [], 0

    # Base query
    query = db.query(Question).filter(
        Question.test_id == test_id, Question.deleted_at.is_(None)
    ).order_by(Question.created_at.desc())

    # Define search configuration
    search_config = {
        "content": {
            "column": Question.content,
            "type": "text",
            "case_sensitive": False,
        },
        "created_at": {"column": Question.created_at, "type": "date"},
        "is_multiple_choice": {
            "column": Question.is_multiple_choice,
            "type": "boolean",
        },
        "category_id": {
            "column": Question.category_id,
            "type": "exact",
        },
    }

    # Apply search filter and pagination
    if request_params:
        paginated_query, total = paginate_query_with_multiple_filters(
            query,
            request_params=request_params,
            search_config=search_config,
            page=page,
            page_size=page_size,
        )
    else:
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
        joinedload(Question.category_obj), joinedload(Question.test_obj)
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
                "category": (
                    question.category_obj.name if question.category_obj else None
                ),
                "test": question.test,
                "is_multiple_choice": question.is_multiple_choice,
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


def get_question_by_test_and_id(
    db: Session,
    test_id: str,
    question_id: str,
):
    """
    Get a specific question by test_id and question_id with answers.

    Args:
        db: Database session
        test_id: Test UUID
        question_id: Question UUID

    Returns:
        Question dict or None if not found
    """
    # Verify test exists
    test = db.query(Test).filter(Test.id == test_id, Test.deleted_at.is_(None)).first()

    if not test:
        return None

    # Get question and verify it belongs to test
    question = (
        db.query(Question)
        .options(joinedload(Question.category_obj), joinedload(Question.test_obj))
        .filter(
            Question.id == question_id,
            Question.test_id == test_id,
            Question.deleted_at.is_(None),
        )
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
        "test": question.test,
        "is_multiple_choice": question.is_multiple_choice,
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
        "test": question.test,
        "is_multiple_choice": question.is_multiple_choice,
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


def question_exists(db: Session, question_id: UUID) -> bool:
    """
    Check if a question exists and is not deleted.

    Args:
        db: Database session
        question_id: Question UUID

    Returns:
        True if question exists, False otherwise
    """
    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.deleted_at.is_(None))
        .first()
    )
    return question is not None


def create_question(
    db: Session,
    content: str,
    image_url: Optional[str] = None,
    category_id: Optional[str] = None,
    test_id: Optional[str] = None,
    is_multiple_choice: bool = False,
):
    """
    Create a new question.

    Args:
        db: Database session
        content: Question content
        image_url: Optional image URL
        category_id: Optional category UUID
        test_id: Optional test UUID
        is_multiple_choice: Whether this question has multiple correct answers

    Returns:
        Question dict or None if category/test not found
    """
    # Verify category exists if provided
    if category_id:
        category = (
            db.query(Category)
            .filter(Category.id == category_id, Category.deleted_at.is_(None))
            .first()
        )
        if not category:
            return None

    # Verify test exists if provided
    if test_id:
        test = (
            db.query(Test).filter(Test.id == test_id, Test.deleted_at.is_(None)).first()
        )
        if not test:
            return None

    question = Question(
        content=content,
        image_url=image_url,
        category_id=category_id,
        test_id=test_id,
        is_multiple_choice=is_multiple_choice,
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    # Load relationships
    question = (
        db.query(Question)
        .options(joinedload(Question.category_obj))
        .filter(Question.id == question.id)
        .first()
    )

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
        "test": question.test,
        "is_multiple_choice": question.is_multiple_choice,
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


def update_question(
    db: Session,
    question_id: str,
    content: Optional[str] = None,
    image_url: Optional[str] = None,
    category_id: Optional[str] = None,
    test_id: Optional[str] = None,
    is_multiple_choice: Optional[bool] = None,
):
    """
    Update a question.

    Args:
        db: Database session
        question_id: Question UUID
        content: Optional new question content
        image_url: Optional new image URL
        category_id: Optional new category UUID
        test_id: Optional new test UUID
        is_multiple_choice: Optional new is_multiple_choice value

    Returns:
        Question dict or None if not found
    """
    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.deleted_at.is_(None))
        .first()
    )

    if not question:
        return None

    # Verify category exists if provided
    if category_id is not None:
        category = (
            db.query(Category)
            .filter(Category.id == category_id, Category.deleted_at.is_(None))
            .first()
        )
        if not category:
            return None
        question.category_id = category_id

    # Verify test exists if provided
    if test_id is not None:
        test = (
            db.query(Test).filter(Test.id == test_id, Test.deleted_at.is_(None)).first()
        )
        if not test:
            return None
        question.test_id = test_id

    # Update fields if provided
    if content is not None:
        question.content = content
    if image_url is not None:
        question.image_url = image_url
    if is_multiple_choice is not None:
        question.is_multiple_choice = is_multiple_choice

    db.commit()
    db.refresh(question)

    # Load relationships
    question = (
        db.query(Question)
        .options(joinedload(Question.category_obj))
        .filter(Question.id == question.id)
        .first()
    )

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
        "test": question.test,
        "is_multiple_choice": question.is_multiple_choice,
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


def delete_question(db: Session, question_id: str):
    """
    Soft delete a question.

    Args:
        db: Database session
        question_id: Question UUID

    Returns:
        bool: True if deleted, False if not found
    """
    from datetime import datetime, timezone

    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.deleted_at.is_(None))
        .first()
    )

    if not question:
        return False

    question.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
