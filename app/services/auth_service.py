# app/services/auth_service.py
from sqlalchemy.orm import Session
from app.repository import auth_repo
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.constants import (
    ERROR_EMAIL_ALREADY_REGISTERED,
    ERROR_INCORRECT_EMAIL_OR_PASSWORD,
    JWT_SUBJECT_KEY,
)
from fastapi import HTTPException, status


def register_user(db: Session, request: RegisterRequest) -> TokenResponse:
    """Register a new user and return an access token."""
    # Check if email already exists
    if auth_repo.email_exists(db, request.user_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_EMAIL_ALREADY_REGISTERED
        )

    # Hash the password
    hashed_password = get_password_hash(request.user_password)

    # Create the user
    user = auth_repo.create_user(
        db=db,
        user_email=request.user_email,
        account_name=request.account_name,
        hashed_password=hashed_password
    )

    # Generate access token
    access_token = create_access_token(data={JWT_SUBJECT_KEY: user.user_email})

    return TokenResponse(access_token=access_token)


def login_user(db: Session, request: LoginRequest) -> TokenResponse:
    """Authenticate a user and return an access token."""
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

    return TokenResponse(access_token=access_token)


def get_user_by_email(db: Session, email: str):
    """Get a user by email."""
    return auth_repo.get_user_by_email(db, email)
