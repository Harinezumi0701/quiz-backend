# app/repository/auth_repo.py
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.users import User
from app.models.refresh_tokens import RefreshToken
from app.utils.user_id_generator import generate_unique_user_id


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get a user by email address."""
    return db.query(User).filter(User.user_email == email).first()


def create_user(db: Session, user_email: str, full_name: str, hashed_password: str) -> User:
    """Create a new user."""
    user_id = generate_unique_user_id(db)
    user = User(
        user_id=user_id,
        user_email=user_email,
        full_name=full_name,
        user_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def email_exists(db: Session, email: str) -> bool:
    """Check if an email already exists."""
    return db.query(User).filter(User.user_email == email).first() is not None


def create_refresh_token(db: Session, user_id: str, token: str, expires_at: datetime) -> RefreshToken:
    """Create a new refresh token."""
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def get_refresh_token_by_token(db: Session, token: str) -> RefreshToken | None:
    """Get a refresh token by token string."""
    return db.query(RefreshToken).filter(RefreshToken.token == token).first()


def delete_refresh_token(db: Session, token: str) -> None:
    """Delete (hard delete) a refresh token."""
    refresh_token = get_refresh_token_by_token(db, token)
    if refresh_token:
        db.delete(refresh_token)
        db.commit()


def delete_user_refresh_tokens(db: Session, user_id: str) -> None:
    """Delete all refresh tokens for a user (hard delete)."""
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.commit()
