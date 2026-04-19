from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from app.repository import user_category_settings_repo
from app.models.categories import Category


ERROR_CATEGORY_NOT_FOUND = "Category not found"
ERROR_SETTINGS_NOT_FOUND = "Settings not found for this category"


def _assert_category_exists(db: Session, category_id: UUID) -> None:
    cat = db.query(Category).filter(
        Category.id == category_id,
        Category.deleted_at.is_(None)
    ).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_CATEGORY_NOT_FOUND,
        )


def list_settings(db: Session, user_id: UUID):
    return user_category_settings_repo.list_by_user(db, user_id)


def get_setting(db: Session, user_id: UUID, category_id: UUID):
    _assert_category_exists(db, category_id)
    result = user_category_settings_repo.get_by_user_and_category(db, user_id, category_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_SETTINGS_NOT_FOUND,
        )
    return result


def upsert_setting(
    db: Session,
    user_id: UUID,
    category_id: UUID,
    questions_per_day: int,
    time_limit: int,
):
    _assert_category_exists(db, category_id)
    return user_category_settings_repo.upsert(
        db, user_id, category_id, questions_per_day, time_limit
    )


def delete_setting(db: Session, user_id: UUID, category_id: UUID):
    _assert_category_exists(db, category_id)
    deleted = user_category_settings_repo.delete_by_user_and_category(db, user_id, category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_SETTINGS_NOT_FOUND,
        )
