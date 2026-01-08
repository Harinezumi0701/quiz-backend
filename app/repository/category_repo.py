# app/repository/category_repo.py
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from app.models.categories import Category
from app.models.questions import Question
from app.models.question_sets import QuestionSet
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


def get_question_sets_by_category_id(
    db: Session,
    category_id: str,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """
    Get all question sets for a specific category with optional filtering and pagination.

    Args:
        db: Database session
        category_id: Category UUID
        search_key: Field to search (name)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (question sets list, total count)
    """
    # Verify category exists
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        return [], 0

    # Base query
    query = db.query(QuestionSet).filter(
        QuestionSet.category_id == category_id,
        QuestionSet.deleted_at.is_(None)
    )

    # Define search configuration
    search_config = {
        "name": {
            "column": QuestionSet.name,
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
    question_sets = paginated_query.all()

    result = []
    for qs in question_sets:
        # Count questions in this set
        question_count = db.query(Question).filter(
            Question.question_set_id == qs.id,
            Question.deleted_at.is_(None)
        ).count()

        result.append({
            'id': qs.id,
            'name': qs.name,
            'category_id': qs.category_id,
            'question_count': question_count,
            'created_at': datetime_to_timestamp(qs.created_at),
            'updated_at': datetime_to_timestamp(qs.updated_at)
        })

    return result, total


def get_all_question_sets(
    db: Session,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list, int]:
    """
    Get all question sets with optional filtering and pagination.

    Args:
        db: Database session
        search_key: Field to search (name)
        search_value: Value to search for
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (question sets list, total count)
    """
    # Base query
    query = db.query(QuestionSet).filter(
        QuestionSet.deleted_at.is_(None)
    )

    # Define search configuration
    search_config = {
        "name": {
            "column": QuestionSet.name,
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
    question_sets = paginated_query.all()

    result = []
    for qs in question_sets:
        # Count questions in this set
        question_count = db.query(Question).filter(
            Question.question_set_id == qs.id,
            Question.deleted_at.is_(None)
        ).count()

        result.append({
            'id': qs.id,
            'name': qs.name,
            'category_id': qs.category_id,
            'question_count': question_count,
            'created_at': datetime_to_timestamp(qs.created_at),
            'updated_at': datetime_to_timestamp(qs.updated_at)
        })

    return result, total


def get_question_set_by_id(
    db: Session,
    category_id: str,
    question_set_id: str,
):
    """
    Get a specific question set by category_id and question_set_id.

    Args:
        db: Database session
        category_id: Category UUID
        question_set_id: Question set UUID

    Returns:
        Question set dict or None if not found
    """
    # Verify category exists
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()

    if not category:
        return None

    # Get question set
    question_set = db.query(QuestionSet).filter(
        QuestionSet.id == question_set_id,
        QuestionSet.category_id == category_id,
        QuestionSet.deleted_at.is_(None)
    ).first()

    if not question_set:
        return None

    # Count questions in this set
    question_count = db.query(Question).filter(
        Question.question_set_id == question_set.id,
        Question.deleted_at.is_(None)
    ).count()

    return {
        'id': question_set.id,
        'name': question_set.name,
        'category_id': question_set.category_id,
        'question_count': question_count,
        'created_at': datetime_to_timestamp(question_set.created_at),
        'updated_at': datetime_to_timestamp(question_set.updated_at)
    }


def get_question_set_by_id_only(
    db: Session,
    question_set_id: str,
):
    """
    Get a specific question set by question_set_id only.

    Args:
        db: Database session
        question_set_id: Question set UUID

    Returns:
        Question set dict or None if not found
    """
    # Get question set
    question_set = db.query(QuestionSet).filter(
        QuestionSet.id == question_set_id,
        QuestionSet.deleted_at.is_(None)
    ).first()

    if not question_set:
        return None

    # Count questions in this set
    question_count = db.query(Question).filter(
        Question.question_set_id == question_set.id,
        Question.deleted_at.is_(None)
    ).count()

    return {
        'id': question_set.id,
        'name': question_set.name,
        'category_id': question_set.category_id,
        'question_count': question_count,
        'created_at': datetime_to_timestamp(question_set.created_at),
        'updated_at': datetime_to_timestamp(question_set.updated_at)
    }
