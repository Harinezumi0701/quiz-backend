# app/services/auth_service.py
import os
import secrets
from datetime import datetime, timedelta, timezone
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
from app.utils.email_service import send_activation_email
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
    ERROR_INVALID_REFRESH_TOKEN,
    ERROR_REFRESH_TOKEN_NOT_FOUND,
    ERROR_REFRESH_TOKEN_EXPIRED,
    ERROR_USER_NOT_FOUND,
    ERROR_ACCOUNT_NOT_ACTIVATED,
    ERROR_INVALID_ACTIVATION_TOKEN,
    ERROR_ACTIVATION_TOKEN_EXPIRED,
    ERROR_ACCOUNT_ALREADY_ACTIVATED,
    JWT_SUBJECT_KEY,
)
from fastapi import HTTPException, status

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def register_user(db: Session, request: RegisterRequest) -> TokenData:
    """Register a new user. Sends activation email; account inactive until confirmed."""
    if auth_repo.email_exists(db, request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_EMAIL_ALREADY_REGISTERED,
        )

    hashed_password = get_password_hash(request.password)
    activation_token = secrets.token_urlsafe(32)
    activation_expires_at = datetime.now(timezone.utc) + timedelta(hours=2)

    user = auth_repo.create_user(
        db=db,
        email=request.email,
        full_name=request.full_name,
        hashed_password=hashed_password,
        is_active=False,
        activation_token=activation_token,
        activation_expires_at=activation_expires_at,
    )

    activation_url = f"{FRONTEND_URL}/activate?token={activation_token}"
    send_activation_email(user.email, activation_url)

    access_token = create_access_token(data={JWT_SUBJECT_KEY: user.email})
    return TokenData(access_token=access_token, refresh_token=None, token_type="bearer")


def activate_account(db: Session, token: str) -> dict:
    """Activate a user account using the emailed token."""
    user = auth_repo.get_user_by_activation_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_INVALID_ACTIVATION_TOKEN,
        )

    expires_at = normalize_to_utc(user.activation_expires_at)
    if expires_at and expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_ACTIVATION_TOKEN_EXPIRED,
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_ACCOUNT_ALREADY_ACTIVATED,
        )

    auth_repo.activate_user(db, user)
    return {"message": "Account activated successfully."}


def login_user(db: Session, request: LoginRequest) -> TokenData:
    """Authenticate a user and return access token. Refresh token only if remember_me is True."""
    # Get user by email
    user = auth_repo.get_user_by_email(db, request.email)

    # Check if user exists and password is correct
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INCORRECT_EMAIL_OR_PASSWORD,
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_ACCOUNT_NOT_ACTIVATED,
        )

    # Generate access token
    access_token = create_access_token(data={JWT_SUBJECT_KEY: user.email})

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
    access_token = create_access_token(data={JWT_SUBJECT_KEY: user.email})

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
