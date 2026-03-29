# app/repository/user_category_access_repo.py
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user_category_access import UserCategoryAccess


def get_categories_for_user(db: Session, user_id: UUID) -> list[UserCategoryAccess]:
    """Get all category access records for a user."""
    return (
        db.query(UserCategoryAccess)
        .filter(UserCategoryAccess.user_id == user_id)
        .all()
    )


def get_access(db: Session, user_id: UUID, category_id: UUID) -> UserCategoryAccess | None:
    """Get a specific access record for a user-category pair."""
    return (
        db.query(UserCategoryAccess)
        .filter(
            UserCategoryAccess.user_id == user_id,
            UserCategoryAccess.category_id == category_id,
        )
        .first()
    )


def grant_access(db: Session, user_id: UUID, category_id: UUID) -> UserCategoryAccess:
    """
    Grant a user access to a category.
    Returns the new access record. Caller is responsible for checking duplicates.
    """
    access = UserCategoryAccess(user_id=user_id, category_id=category_id)
    db.add(access)
    db.commit()
    db.refresh(access)
    return access


def revoke_access(db: Session, user_id: UUID, category_id: UUID) -> bool:
    """
    Revoke a user's access to a category.
    Returns True if deleted, False if not found.
    """
    access = get_access(db, user_id, category_id)
    if not access:
        return False
    db.delete(access)
    db.commit()
    return True
