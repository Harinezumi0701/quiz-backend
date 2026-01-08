# app/repository/question_repo.py
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, Tuple
from app.models.questions import Question
from app.models.answer_options import AnswerOption
from app.models.categories import Category
from app.models.tests import Test
from app.utils.search_pagination import paginate_query
from app.utils.datetime_utils import datetime_to_timestamp


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
        .options(joinedload(Question.category_obj), joinedload(Question.test_obj))
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
                "category": question.category_obj.name if question.category_obj else None,
                "test": question.test,
                "is_multiple_choice": question.is_multiple_choice,
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
        search_key: Field to search (content, created_at, test)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (questions list, total count)
    """
    # Always join with Test (left outer join) to enable test search
    query = (
        db.query(Question)
        .outerjoin(Test, Question.test_id == Test.id)
        .filter(Question.deleted_at.is_(None))
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
    questions = paginated_query.options(
        joinedload(Question.category_obj),
        joinedload(Question.test_obj)
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
                "category": question.category_obj.name if question.category_obj else None,
                "test": question.test,
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


def get_questions_by_category_and_test_id(
    db: Session,
    category_id: str,
    test_id: str,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
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

    Returns:
        Tuple of (questions list, total count)
    """
    # Verify category exists
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        return [], 0

    # Verify test exists and belongs to category
    test = db.query(Test).filter(
        Test.id == test_id,
        Test.category_id == category_id,
        Test.deleted_at.is_(None)
    ).first()

    if not test:
        return [], 0

    # Base query
    query = (
        db.query(Question)
        .filter(
            Question.category_id == category_id,
            Question.test_id == test_id,
            Question.deleted_at.is_(None)
        )
    )

    # Define search configuration
    search_config = {
        "content": {
            "column": Question.content,
            "type": "text",
            "case_sensitive": False,
        },
        "created_at": {"column": Question.created_at, "type": "date"},
    }

    # Apply search filter and pagination
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
        joinedload(Question.category_obj),
        joinedload(Question.test_obj)
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
                "category": question.category_obj.name if question.category_obj else None,
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

    Returns:
        Tuple of (questions list, total count)
    """
    # Verify test exists
    test = db.query(Test).filter(
        Test.id == test_id,
        Test.deleted_at.is_(None)
    ).first()

    if not test:
        return [], 0

    # Base query
    query = (
        db.query(Question)
        .filter(
            Question.test_id == test_id,
            Question.deleted_at.is_(None)
        )
    )

    # Define search configuration
    search_config = {
        "content": {
            "column": Question.content,
            "type": "text",
            "case_sensitive": False,
        },
        "created_at": {"column": Question.created_at, "type": "date"},
    }

    # Apply search filter and pagination
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
        joinedload(Question.category_obj),
        joinedload(Question.test_obj)
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
                "category": question.category_obj.name if question.category_obj else None,
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
    test = db.query(Test).filter(
        Test.id == test_id,
        Test.deleted_at.is_(None)
    ).first()

    if not test:
        return None

    # Get question and verify it belongs to test
    question = (
        db.query(Question)
        .options(joinedload(Question.category_obj), joinedload(Question.test_obj))
        .filter(
            Question.id == question_id,
            Question.test_id == test_id,
            Question.deleted_at.is_(None)
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


def get_answers_by_question_id(
    db: Session,
    question_id: str,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """
    Get all answers for a specific question with optional filtering and pagination.

    Args:
        db: Database session
        question_id: Question UUID
        search_key: Field to search (content, is_correct)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (answers list, total count)
    """
    # Verify question exists
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.deleted_at.is_(None)
    ).first()

    if not question:
        return [], 0

    # Base query
    query = db.query(AnswerOption).filter(
        AnswerOption.question_id == question_id,
        AnswerOption.deleted_at.is_(None)
    )

    # Handle boolean search for is_correct separately
    if search_key == "is_correct" and search_value:
        # Convert string to boolean
        is_correct_value = search_value.lower() in ("true", "1", "yes", "t")
        query = query.filter(AnswerOption.is_correct == is_correct_value)
    else:
        # Define search configuration for other fields
        search_config = {
            "content": {
                "column": AnswerOption.content,
                "type": "text",
                "case_sensitive": False,
            },
        }

        # Apply search filter
        if search_config and search_key in search_config:
            from app.utils.search_pagination import SearchFilter
            search_filter = SearchFilter(search_config)
            query = search_filter.apply(query, search_key, search_value)

    # Apply pagination
    from app.utils.search_pagination import PaginationHandler
    paginated_query, total = PaginationHandler.apply(query, page, page_size)

    # Execute query
    answers = paginated_query.all()

    result = []
    for answer in answers:
        result.append({
            'id': answer.id,
            'question_id': answer.question_id,
            'content': answer.content,
            'is_correct': answer.is_correct,
            'explanation': answer.explanation,
            'created_at': datetime_to_timestamp(answer.created_at),
            'updated_at': datetime_to_timestamp(answer.updated_at)
        })

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
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.deleted_at.is_(None)
    ).first()

    if not question:
        return None

    # Get answer
    answer = db.query(AnswerOption).filter(
        AnswerOption.id == answer_id,
        AnswerOption.question_id == question_id,
        AnswerOption.deleted_at.is_(None)
    ).first()

    if not answer:
        return None

    return {
        'id': answer.id,
        'question_id': answer.question_id,
        'content': answer.content,
        'is_correct': answer.is_correct,
        'explanation': answer.explanation,
        'created_at': datetime_to_timestamp(answer.created_at),
        'updated_at': datetime_to_timestamp(answer.updated_at)
    }


def get_all_answers(
    db: Session,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """
    Get all answers with optional filtering and pagination.

    Args:
        db: Database session
        search_key: Field to search (content, is_correct, question_id)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (answers list, total count)
    """
    # Base query
    query = db.query(AnswerOption).filter(
        AnswerOption.deleted_at.is_(None)
    )

    # Handle boolean search for is_correct separately
    if search_key == "is_correct" and search_value:
        # Convert string to boolean
        is_correct_value = search_value.lower() in ("true", "1", "yes", "t")
        query = query.filter(AnswerOption.is_correct == is_correct_value)
    elif search_key == "question_id" and search_value:
        # Handle UUID search for question_id
        try:
            query = query.filter(AnswerOption.question_id == search_value)
        except (ValueError, TypeError):
            # Invalid UUID format, return empty result
            return [], 0
    else:
        # Define search configuration for other fields
        search_config = {
            "content": {
                "column": AnswerOption.content,
                "type": "text",
                "case_sensitive": False,
            },
        }

        # Apply search filter
        if search_config and search_key in search_config:
            from app.utils.search_pagination import SearchFilter
            search_filter = SearchFilter(search_config)
            query = search_filter.apply(query, search_key, search_value)

    # Apply pagination
    from app.utils.search_pagination import PaginationHandler
    paginated_query, total = PaginationHandler.apply(query, page, page_size)

    # Execute query
    answers = paginated_query.all()

    result = []
    for answer in answers:
        result.append({
            'id': answer.id,
            'question_id': answer.question_id,
            'content': answer.content,
            'is_correct': answer.is_correct,
            'explanation': answer.explanation,
            'created_at': datetime_to_timestamp(answer.created_at),
            'updated_at': datetime_to_timestamp(answer.updated_at)
        })

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
    answer = db.query(AnswerOption).filter(
        AnswerOption.id == answer_id,
        AnswerOption.deleted_at.is_(None)
    ).first()

    if not answer:
        return None

    return {
        'id': answer.id,
        'question_id': answer.question_id,
        'content': answer.content,
        'is_correct': answer.is_correct,
        'explanation': answer.explanation,
        'created_at': datetime_to_timestamp(answer.created_at),
        'updated_at': datetime_to_timestamp(answer.updated_at)
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
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.deleted_at.is_(None)
    ).first()
    return question is not None


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
    answer = db.query(AnswerOption).filter(
        AnswerOption.id == answer_id,
        AnswerOption.question_id == question_id,
        AnswerOption.deleted_at.is_(None)
    ).first()
    return answer is not None
