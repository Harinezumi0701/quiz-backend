# app/repository/category_repo.py
from sqlalchemy.orm import Session
from typing import Optional
from app.models.categories import Category
from app.models.questions import Question


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
            'created_at': category.created_at,
            'updated_at': category.updated_at
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
        'created_at': category.created_at,
        'updated_at': category.updated_at
    }
