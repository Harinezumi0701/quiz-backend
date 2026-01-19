# app/repository/category_repo.py
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from app.models.categories import Category
from app.models.questions import Question
from app.utils.datetime_utils import datetime_to_timestamp
from app.utils.search_pagination import paginate_query_with_multiple_filters
from typing import Dict, Any


def get_all_categories_with_search(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """Get all categories with optional name search and pagination."""
    query = db.query(Category).filter(Category.deleted_at.is_(None)).order_by(Category.created_at.desc())

    # Define search configuration
    search_config = {
        "name": {
            "column": Category.name,
            "type": "text",
            "case_sensitive": False,
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

    categories = paginated_query.all()

    result = []
    for category in categories:
        count = (
            db.query(Question)
            .filter(Question.category_id == category.id, Question.deleted_at.is_(None))
            .count()
        )

        result.append(
            {
                "id": category.id,
                "name": category.name,
                "question_count": count,
                "created_at": datetime_to_timestamp(category.created_at),
                "updated_at": datetime_to_timestamp(category.updated_at),
            }
        )

    return result, total


def get_category_by_id(db: Session, category_id: str):
    """Get a specific category by ID."""
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.deleted_at.is_(None))
        .first()
    )

    if not category:
        return None

    count = (
        db.query(Question)
        .filter(Question.category_id == category.id, Question.deleted_at.is_(None))
        .count()
    )

    return {
        "id": category.id,
        "name": category.name,
        "question_count": count,
        "created_at": datetime_to_timestamp(category.created_at),
        "updated_at": datetime_to_timestamp(category.updated_at),
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

    count = (
        db.query(Question)
        .filter(Question.category_id == category.id, Question.deleted_at.is_(None))
        .count()
    )

    return {
        "id": category.id,
        "name": category.name,
        "question_count": count,
        "created_at": datetime_to_timestamp(category.created_at),
        "updated_at": datetime_to_timestamp(category.updated_at),
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
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.deleted_at.is_(None))
        .first()
    )

    if not category:
        return None

    category.name = name
    db.commit()
    db.refresh(category)

    count = (
        db.query(Question)
        .filter(Question.category_id == category.id, Question.deleted_at.is_(None))
        .count()
    )

    return {
        "id": category.id,
        "name": category.name,
        "question_count": count,
        "created_at": datetime_to_timestamp(category.created_at),
        "updated_at": datetime_to_timestamp(category.updated_at),
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

    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.deleted_at.is_(None))
        .first()
    )

    if not category:
        return False

    category.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
