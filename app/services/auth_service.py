# app/services/auth_service.py
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repository import auth_repo
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_refresh_token_expires_delta,
)
from app.utils.datetime_utils import normalize_to_utc
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenData,
    RefreshTokenRequest,
    RevokeTokenRequest,
)
from app.constants import (
    ERROR_EMAIL_ALREADY_REGISTERED,
    ERROR_INCORRECT_EMAIL_OR_PASSWORD,
    ERROR_REFRESH_TOKEN_NOT_FOUND,
    ERROR_REFRESH_TOKEN_EXPIRED,
    ERROR_USER_NOT_FOUND,
    JWT_SUBJECT_KEY,
)
from fastapi import HTTPException, status


def register_user(db: Session, request: RegisterRequest) -> TokenData:
    """Register a new user and return access token (no refresh token)."""
    # Check if email already exists
    if auth_repo.email_exists(db, request.user_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_EMAIL_ALREADY_REGISTERED,
        )

    # Hash the password
    hashed_password = get_password_hash(request.user_password)

    # Create the user
    user = auth_repo.create_user(
        db=db,
        user_email=request.user_email,
        full_name=request.full_name,
        hashed_password=hashed_password,
    )

    # Generate access token
    access_token = create_access_token(data={JWT_SUBJECT_KEY: user.user_email})

    return TokenData(access_token=access_token, refresh_token=None, token_type="bearer")


def login_user(db: Session, request: LoginRequest) -> TokenData:
    """Authenticate a user and return access token. Refresh token only if remember_me is True."""
    # Get user by email
    user = auth_repo.get_user_by_email(db, request.user_email)

    # Check if user exists and password is correct
    if not user or not verify_password(request.user_password, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INCORRECT_EMAIL_OR_PASSWORD,
        )

    # Generate access token
    access_token = create_access_token(data={JWT_SUBJECT_KEY: user.user_email})

    # Generate and save refresh token only if remember_me is True
    refresh_token_str = None
    if request.remember_me:
        refresh_token_str = create_refresh_token()
        expires_at = datetime.now(timezone.utc) + get_refresh_token_expires_delta()
        auth_repo.create_refresh_token(
            db=db, user_id=user.id, token=refresh_token_str, expires_at=expires_at
        )

    return TokenData(
        access_token=access_token, refresh_token=refresh_token_str, token_type="bearer"
    )


def get_user_by_email(db: Session, email: str):
    """Get a user by email."""
    return auth_repo.get_user_by_email(db, email)


def refresh_access_token(db: Session, request: RefreshTokenRequest) -> TokenData:
    """Refresh access token using refresh token. Old refresh token is deleted and new one is generated."""
    # Get refresh token from database
    refresh_token = auth_repo.get_refresh_token_by_token(db, request.refresh_token)

    # Check if refresh token exists and is valid
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_REFRESH_TOKEN
        )

    # Check if refresh token is expired
    expires_at_utc = normalize_to_utc(refresh_token.expires_at)
    if expires_at_utc and expires_at_utc < datetime.now(timezone.utc):
        # Delete expired token
        auth_repo.delete_refresh_token(db, request.refresh_token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_REFRESH_TOKEN_EXPIRED
        )

    # Get user
    user = refresh_token.user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_USER_NOT_FOUND
        )

    # Generate new access token
    access_token = create_access_token(data={JWT_SUBJECT_KEY: user.user_email})

    # Delete old refresh token
    auth_repo.delete_refresh_token(db, request.refresh_token)

    # Generate and save new refresh token
    new_refresh_token_str = create_refresh_token()
    expires_at = datetime.now(timezone.utc) + get_refresh_token_expires_delta()
    auth_repo.create_refresh_token(
        db=db, user_id=user.id, token=new_refresh_token_str, expires_at=expires_at
    )

    return TokenData(
        access_token=access_token,
        refresh_token=new_refresh_token_str,
        token_type="bearer",
    )


def revoke_token(db: Session, request: RevokeTokenRequest) -> None:
    """Revoke a refresh token."""
    # Get refresh token from database
    refresh_token = auth_repo.get_refresh_token_by_token(db, request.refresh_token)

    # Check if refresh token exists
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_REFRESH_TOKEN_NOT_FOUND
        )

    # Delete (soft delete) the refresh token
    auth_repo.delete_refresh_token(db, request.refresh_token)
