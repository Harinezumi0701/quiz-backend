# app/api/v1/auth.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RevokeTokenRequest,
    TokenResponse,
)
from app.schemas.http_response import ErrorResponse
from app.services import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new account and return access token",
    responses={
        201: {
            "description": "Registration successful",
        },
        400: {
            "description": "Email already registered",
            "model": ErrorResponse,
        }
    }
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.

    - **email**: User email (must be a valid email)
    - **full_name**: Full name
    - **password**: Password (minimum 6 characters)

    After successful registration, you will receive an access token to use for other APIs.
    """
    token_data = auth_service.register_user(db, request)
    return TokenResponse(data=token_data, meta={})


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate user and return access token",
    responses={
        200: {
            "description": "Login successful",
        },
        401: {
            "description": "Incorrect email or password",
            "model": ErrorResponse,
        }
    }
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.

    - **email**: Registered email
    - **password**: Account password
    - **remember_me**: (Optional) If true, returns refresh token for persistent sessions

    Returns access token. Refresh token is only returned if remember_me is true.
    """
    token_data = auth_service.login_user(db, request)
    return TokenResponse(data=token_data, meta={})


@router.post(
    "/token/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Refresh access token using refresh token",
    responses={
        200: {
            "description": "Token refreshed successfully",
        },
        401: {
            "description": "Invalid or expired refresh token",
            "model": ErrorResponse,
        }
    }
)
def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.

    - **refresh_token**: Valid refresh token

    Returns new access token and new refresh token. Old refresh token is invalidated.
    """
    token_data = auth_service.refresh_access_token(db, request)
    return TokenResponse(data=token_data, meta={})


@router.post(
    "/token/revoke",
    status_code=status.HTTP_200_OK,
    summary="Revoke refresh token",
    description="Revoke a refresh token to invalidate it",
    responses={
        200: {
            "description": "Token revoked successfully",
        },
        401: {
            "description": "Invalid refresh token",
            "model": ErrorResponse,
        }
    }
)
def revoke(request: RevokeTokenRequest, db: Session = Depends(get_db)):
    """
    Revoke a refresh token.

    - **refresh_token**: Refresh token to revoke

    Invalidates the refresh token so it can no longer be used to refresh access tokens.
    """
    auth_service.revoke_token(db, request)
    return {"message": "Token revoked successfully"}
