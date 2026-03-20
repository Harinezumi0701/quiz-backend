# app/services/category_access_service.py
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repository import user_category_access_repo, category_repo, user_repo
from app.models.user_category_access import UserCategoryAccess


def list_user_category_access(db: Session, user_id: UUID) -> list[UserCategoryAccess]:
    """List all categories a user has access to."""
    _assert_user_exists(db, user_id)
    return user_category_access_repo.get_categories_for_user(db, user_id)


def grant_category_access(db: Session, user_id: UUID, category_id: UUID) -> UserCategoryAccess:
    """Grant a user access to a category. Raises 404 if user/category not found, 409 if already granted."""
    _assert_user_exists(db, user_id)
    _assert_category_exists(db, category_id)

    existing = user_category_access_repo.get_access(db, user_id, category_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has access to this category",
        )

    return user_category_access_repo.grant_access(db, user_id, category_id)


def revoke_category_access(db: Session, user_id: UUID, category_id: UUID) -> None:
    """Revoke a user's access to a category. Raises 404 if not found."""
    _assert_user_exists(db, user_id)

    deleted = user_category_access_repo.revoke_access(db, user_id, category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category access not found for this user",
        )


def _assert_user_exists(db: Session, user_id: UUID) -> None:
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )


def _assert_category_exists(db: Session, category_id: UUID) -> None:
    category = category_repo.get_category_by_id(db, str(category_id))
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
