# app/repository/user_repo.py
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.users import User

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: UUID):
    """Get user by UUID id."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_user_id(db: Session, user_id: str):
    """Get user by user_id (editable unique identifier)."""
    return db.query(User).filter(User.user_id == user_id).first()

def user_id_exists(db: Session, user_id: str, exclude_user_id: UUID = None) -> bool:
    """Check if user_id already exists, optionally excluding a specific user."""
    query = db.query(User).filter(User.user_id == user_id)
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    return query.first() is not None

def update_user(db: Session, user: User, **kwargs):
    """Update user fields."""
    for key, value in kwargs.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
