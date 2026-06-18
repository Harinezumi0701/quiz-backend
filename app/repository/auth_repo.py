# app/repository/auth_repo.py
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.users import User
from app.models.refresh_tokens import RefreshToken
from app.utils.user_id_generator import generate_unique_user_id
from app.repository.role_repo import get_default_role


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get a user by email address."""
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    email: str,
    full_name: str,
    hashed_password: str,
    is_active: bool = False,
    activation_token: str | None = None,
    activation_expires_at: datetime | None = None,
) -> User:
    """Create a new user."""
    user_id = generate_unique_user_id(db)

    # Get default role if exists
    default_role = get_default_role(db)
    role_id = default_role.id if default_role else None

    user = User(
        user_id=user_id,
        email=email,
        full_name=full_name,
        password=hashed_password,
        role_id=role_id,
        is_active=is_active,
        activation_token=activation_token,
        activation_expires_at=activation_expires_at,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_activation_token(db: Session, token: str) -> User | None:
    """Get a user by activation token."""
    return db.query(User).filter(User.activation_token == token).first()


def activate_user(db: Session, user: User) -> User:
    """Mark user as active and clear activation token fields."""
    user.is_active = True
    user.activation_token = None
    user.activation_expires_at = None
    db.commit()
    db.refresh(user)
    return user


def email_exists(db: Session, email: str) -> bool:
    """Check if an email already exists."""
    return db.query(User).filter(User.email == email).first() is not None


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
