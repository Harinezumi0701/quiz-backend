# app/repository/test_repo.py
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from app.models.categories import Category
from app.models.questions import Question
from app.models.tests import Test
from app.utils.datetime_utils import datetime_to_timestamp
from app.utils.search_pagination import paginate_query_with_multiple_filters
from typing import Dict, Any


def get_tests_by_category_id(
    db: Session,
    category_id: str,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all tests for a specific category with optional filtering and pagination.

    Args:
        db: Database session
        category_id: Category UUID
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for multiple filters

    Returns:
        Tuple of (tests list, total count)
    """
    # Verify category exists
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.deleted_at.is_(None))
        .first()
    )

    if not category:
        return [], 0

    # Base query
    query = db.query(Test).filter(
        Test.category_id == category_id, Test.deleted_at.is_(None)
    ).order_by(Test.created_at.desc())

    # Define search configuration
    search_config = {
        "name": {
            "column": Test.name,
            "type": "text",
            "case_sensitive": False,
        },
    }

    # Apply search filter and pagination
    # Apply search filter and pagination
    paginated_query, total = paginate_query_with_multiple_filters(
        query,
        request_params=request_params or {},
        search_config=search_config,
        page=page,
        page_size=page_size,
    )

    # Execute query
    tests = paginated_query.all()

    result = []
    for test in tests:
        # Count questions in this test
        question_count = (
            db.query(Question)
            .filter(Question.test_id == test.id, Question.deleted_at.is_(None))
            .count()
        )

        result.append(
            {
                "id": test.id,
                "name": test.name,
                "category_id": test.category_id,
                "description": test.description,
                "time_limit": test.time_limit,
                "question_count": question_count,
                "created_at": datetime_to_timestamp(test.created_at),
                "updated_at": datetime_to_timestamp(test.updated_at),
            }
        )

    return result, total


def get_all_tests(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all tests with optional filtering and pagination.

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for multiple filters

    Returns:
        Tuple of (tests list, total count)
    """
    # Base query
    query = db.query(Test).filter(Test.deleted_at.is_(None)).order_by(Test.created_at.desc())

    # Define search configuration
    search_config = {
        "name": {
            "column": Test.name,
            "type": "text",
            "case_sensitive": False,
        },
        "category_id": {
            "column": Test.category_id,
            "type": "exact",
        },
    }

    # Apply search filter and pagination
    # Apply search filter and pagination
    paginated_query, total = paginate_query_with_multiple_filters(
        query,
        request_params=request_params or {},
        search_config=search_config,
        page=page,
        page_size=page_size,
    )

    # Execute query
    tests = paginated_query.all()

    result = []
    for test in tests:
        # Count questions in this test
        question_count = (
            db.query(Question)
            .filter(Question.test_id == test.id, Question.deleted_at.is_(None))
            .count()
        )

        result.append(
            {
                "id": test.id,
                "name": test.name,
                "category_id": test.category_id,
                "description": test.description,
                "time_limit": test.time_limit,
                "question_count": question_count,
                "created_at": datetime_to_timestamp(test.created_at),
                "updated_at": datetime_to_timestamp(test.updated_at),
            }
        )

    return result, total


def get_test_by_id(
    db: Session,
    category_id: str,
    test_id: str,
):
    """
    Get a specific test by category_id and test_id.

    Args:
        db: Database session
        category_id: Category UUID
        test_id: Test UUID

    Returns:
        Test dict or None if not found
    """
    # Verify category exists
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.deleted_at.is_(None))
        .first()
    )

    if not category:
        return None

    # Get test
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
        return None

    # Count questions in this test
    question_count = (
        db.query(Question)
        .filter(Question.test_id == test.id, Question.deleted_at.is_(None))
        .count()
    )

    return {
        "id": test.id,
        "name": test.name,
        "category_id": test.category_id,
        "description": test.description,
        "time_limit": test.time_limit,
        "question_count": question_count,
        "created_at": datetime_to_timestamp(test.created_at),
        "updated_at": datetime_to_timestamp(test.updated_at),
    }


def get_test_by_id_only(
    db: Session,
    test_id: str,
):
    """
    Get a specific test by test_id only.

    Args:
        db: Database session
        test_id: Test UUID

    Returns:
        Test dict or None if not found
    """
    # Get test
    test = db.query(Test).filter(Test.id == test_id, Test.deleted_at.is_(None)).first()

    if not test:
        return None

    # Count questions in this test
    question_count = (
        db.query(Question)
        .filter(Question.test_id == test.id, Question.deleted_at.is_(None))
        .count()
    )

    return {
        "id": test.id,
        "name": test.name,
        "category_id": test.category_id,
        "description": test.description,
        "time_limit": test.time_limit,
        "question_count": question_count,
        "created_at": datetime_to_timestamp(test.created_at),
        "updated_at": datetime_to_timestamp(test.updated_at),
    }


def create_test(
    db: Session,
    name: str,
    category_id: str,
    time_limit: int,
    description: str | None = None,
):
    """
    Create a new test.

    Args:
        db: Database session
        name: Test name
        category_id: Category UUID
        time_limit: Time limit in minutes (required)
        description: Test description (optional)

    Returns:
        Test dict or None if category not found
    """
    # Verify category exists
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.deleted_at.is_(None))
        .first()
    )

    if not category:
        return None

    test = Test(
        name=name,
        category_id=category_id,
        description=description,
        time_limit=time_limit,
    )
    db.add(test)
    db.commit()
    db.refresh(test)

    # Count questions in this test
    question_count = (
        db.query(Question)
        .filter(Question.test_id == test.id, Question.deleted_at.is_(None))
        .count()
    )

    return {
        "id": test.id,
        "name": test.name,
        "category_id": test.category_id,
        "description": test.description,
        "time_limit": test.time_limit,
        "question_count": question_count,
        "created_at": datetime_to_timestamp(test.created_at),
        "updated_at": datetime_to_timestamp(test.updated_at),
    }


def update_test(
    db: Session,
    test_id: str,
    name: str,
    time_limit: int,
    description: str | None = None,
):
    """
    Update a test.

    Args:
        db: Database session
        test_id: Test UUID
        name: New test name
        time_limit: Time limit in minutes (required)
        description: Test description (optional)

    Returns:
        Test dict or None if not found
    """
    test = db.query(Test).filter(Test.id == test_id, Test.deleted_at.is_(None)).first()

    if not test:
        return None

    test.name = name
    test.time_limit = time_limit
    if description is not None:
        test.description = description
    db.commit()
    db.refresh(test)

    # Count questions in this test
    question_count = (
        db.query(Question)
        .filter(Question.test_id == test.id, Question.deleted_at.is_(None))
        .count()
    )

    return {
        "id": test.id,
        "name": test.name,
        "category_id": test.category_id,
        "description": test.description,
        "time_limit": test.time_limit,
        "question_count": question_count,
        "created_at": datetime_to_timestamp(test.created_at),
        "updated_at": datetime_to_timestamp(test.updated_at),
    }


def delete_test(db: Session, test_id: str):
    """
    Soft delete a test.

    Args:
        db: Database session
        test_id: Test UUID

    Returns:
        bool: True if deleted, False if not found
    """
    from datetime import datetime, timezone

    test = db.query(Test).filter(Test.id == test_id, Test.deleted_at.is_(None)).first()

    if not test:
        return False

    test.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
