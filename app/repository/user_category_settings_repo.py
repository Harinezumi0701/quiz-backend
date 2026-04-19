from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from app.models.user_category_settings import UserCategorySettings
from app.utils.datetime_utils import datetime_to_timestamp


def _to_dict(settings: UserCategorySettings) -> dict:
    return {
        "id": settings.id,
        "user_id": settings.user_id,
        "category_id": settings.category_id,
        "category_name": settings.category.name if settings.category else None,
        "questions_per_day": settings.questions_per_day,
        "time_limit": settings.time_limit,
        "created_at": datetime_to_timestamp(settings.created_at),
        "updated_at": datetime_to_timestamp(settings.updated_at),
    }


def get_by_user_and_category(
    db: Session, user_id: UUID, category_id: UUID
) -> Optional[dict]:
    row = (
        db.query(UserCategorySettings)
        .filter(
            UserCategorySettings.user_id == user_id,
            UserCategorySettings.category_id == category_id,
        )
        .first()
    )
    return _to_dict(row) if row else None


def list_by_user(db: Session, user_id: UUID) -> List[dict]:
    rows = (
        db.query(UserCategorySettings)
        .filter(UserCategorySettings.user_id == user_id)
        .order_by(UserCategorySettings.created_at.desc())
        .all()
    )
    return [_to_dict(r) for r in rows]


def upsert(
    db: Session,
    user_id: UUID,
    category_id: UUID,
    questions_per_day: int,
    time_limit: int,
) -> dict:
    row = (
        db.query(UserCategorySettings)
        .filter(
            UserCategorySettings.user_id == user_id,
            UserCategorySettings.category_id == category_id,
        )
        .first()
    )
    if row:
        row.questions_per_day = questions_per_day
        row.time_limit = time_limit
    else:
        row = UserCategorySettings(
            user_id=user_id,
            category_id=category_id,
            questions_per_day=questions_per_day,
            time_limit=time_limit,
        )
        db.add(row)
    db.commit()
    db.refresh(row)
    return _to_dict(row)


def delete_by_user_and_category(
    db: Session, user_id: UUID, category_id: UUID
) -> bool:
    row = (
        db.query(UserCategorySettings)
        .filter(
            UserCategorySettings.user_id == user_id,
            UserCategorySettings.category_id == category_id,
        )
        .first()
    )
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True
