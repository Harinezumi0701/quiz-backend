# app/repository/category_repo.py
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from app.models.categories import Category
from app.models.questions import Question
from app.models.tests import Test
from app.utils.datetime_utils import datetime_to_timestamp
from app.utils.search_pagination import paginate_query


def get_all_categories_with_search(
    db: Session,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None
):
    """Get all categories with optional name search."""
    query = db.query(Category).filter(Category.deleted_at.is_(None))
    
    # Apply search filter
    if search_key == "name" and search_value:
        query = query.filter(Category.name.ilike(f"%{search_value}%"))
    
    categories = query.all()
    
    result = []
    for category in categories:
        count = db.query(Question).filter(
            Question.category_id == category.id,
            Question.deleted_at.is_(None)
        ).count()
        
        result.append({
            'id': category.id,
            'name': category.name,
            'question_count': count,
            'created_at': datetime_to_timestamp(category.created_at),
            'updated_at': datetime_to_timestamp(category.updated_at)
        })
    
    return result


def get_category_by_id(db: Session, category_id: str):
    """Get a specific category by ID."""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()
    
    if not category:
        return None
    
    count = db.query(Question).filter(
        Question.category_id == category.id,
        Question.deleted_at.is_(None)
    ).count()
    
    return {
        'id': category.id,
        'name': category.name,
        'question_count': count,
        'created_at': datetime_to_timestamp(category.created_at),
        'updated_at': datetime_to_timestamp(category.updated_at)
    }


def get_tests_by_category_id(
    db: Session,
    category_id: str,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """
    Get all tests for a specific category with optional filtering and pagination.

    Args:
        db: Database session
        category_id: Category UUID
        search_key: Field to search (name)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (tests list, total count)
    """
    # Verify category exists
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        return [], 0

    # Base query
    query = db.query(Test).filter(
        Test.category_id == category_id,
        Test.deleted_at.is_(None)
    )

    # Define search configuration
    search_config = {
        "name": {
            "column": Test.name,
            "type": "text",
            "case_sensitive": False,
        },
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

    # Execute query
    tests = paginated_query.all()

    result = []
    for test in tests:
        # Count questions in this test
        question_count = db.query(Question).filter(
            Question.test_id == test.id,
            Question.deleted_at.is_(None)
        ).count()

        result.append({
            'id': test.id,
            'name': test.name,
            'category_id': test.category_id,
            'question_count': question_count,
            'created_at': datetime_to_timestamp(test.created_at),
            'updated_at': datetime_to_timestamp(test.updated_at)
        })

    return result, total


def get_all_tests(
    db: Session,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """
    Get all tests with optional filtering and pagination.

    Args:
        db: Database session
        search_key: Field to search (name)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (tests list, total count)
    """
    # Base query
    query = db.query(Test).filter(
        Test.deleted_at.is_(None)
    )

    # Define search configuration
    search_config = {
        "name": {
            "column": Test.name,
            "type": "text",
            "case_sensitive": False,
        },
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

    # Execute query
    tests = paginated_query.all()

    result = []
    for test in tests:
        # Count questions in this test
        question_count = db.query(Question).filter(
            Question.test_id == test.id,
            Question.deleted_at.is_(None)
        ).count()

        result.append({
            'id': test.id,
            'name': test.name,
            'category_id': test.category_id,
            'question_count': question_count,
            'created_at': datetime_to_timestamp(test.created_at),
            'updated_at': datetime_to_timestamp(test.updated_at)
        })

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
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        return None

    # Get test
    test = db.query(Test).filter(
        Test.id == test_id,
        Test.category_id == category_id,
        Test.deleted_at.is_(None)
    ).first()

    if not test:
        return None

    # Count questions in this test
    question_count = db.query(Question).filter(
        Question.test_id == test.id,
        Question.deleted_at.is_(None)
    ).count()

    return {
        'id': test.id,
        'name': test.name,
        'category_id': test.category_id,
        'question_count': question_count,
        'created_at': datetime_to_timestamp(test.created_at),
        'updated_at': datetime_to_timestamp(test.updated_at)
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
    test = db.query(Test).filter(
        Test.id == test_id,
        Test.deleted_at.is_(None)
    ).first()

    if not test:
        return None

    # Count questions in this test
    question_count = db.query(Question).filter(
        Question.test_id == test.id,
        Question.deleted_at.is_(None)
    ).count()

    return {
        'id': test.id,
        'name': test.name,
        'category_id': test.category_id,
        'question_count': question_count,
        'created_at': datetime_to_timestamp(test.created_at),
        'updated_at': datetime_to_timestamp(test.updated_at)
    }


def create_category(db: Session, name: str):
    """
    Create a new category.

    Args:
        db: Database session
        name: Category name

    Returns:
        Category dict
    """
    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)

    count = db.query(Question).filter(
        Question.category_id == category.id,
        Question.deleted_at.is_(None)
    ).count()

    return {
        'id': category.id,
        'name': category.name,
        'question_count': count,
        'created_at': datetime_to_timestamp(category.created_at),
        'updated_at': datetime_to_timestamp(category.updated_at)
    }


def update_category(db: Session, category_id: str, name: str):
    """
    Update a category.

    Args:
        db: Database session
        category_id: Category UUID
        name: New category name

    Returns:
        Category dict or None if not found
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        return None

    category.name = name
    db.commit()
    db.refresh(category)

    count = db.query(Question).filter(
        Question.category_id == category.id,
        Question.deleted_at.is_(None)
    ).count()

    return {
        'id': category.id,
        'name': category.name,
        'question_count': count,
        'created_at': datetime_to_timestamp(category.created_at),
        'updated_at': datetime_to_timestamp(category.updated_at)
    }


def delete_category(db: Session, category_id: str):
    """
    Soft delete a category.

    Args:
        db: Database session
        category_id: Category UUID

    Returns:
        bool: True if deleted, False if not found
    """
    from datetime import datetime, timezone

    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        return False

    category.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
