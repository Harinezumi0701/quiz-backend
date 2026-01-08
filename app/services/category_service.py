# app/services/category_service.py
from sqlalchemy.orm import Session
from app.repository import category_repo


def get_all_categories_with_search(db: Session, search_key: str = None, search_value: str = None):
    """Get all categories with optional name search."""
    return category_repo.get_all_categories_with_search(db, search_key, search_value)


def get_category_by_id(db: Session, category_id: str):
    """Get a specific category by ID."""
    return category_repo.get_category_by_id(db, category_id)
