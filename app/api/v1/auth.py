# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services import auth_service
from app.db.session import get_db
from app.constants import HTTP_STATUS_CREATED

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=HTTP_STATUS_CREATED,
    summary="Register new user",
    description="Create a new account and return access token",
    responses={
        201: {
            "description": "Registration successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        400: {
            "description": "Email already registered",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        }
    }
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.

    - **user_email**: User email (must be a valid email)
    - **account_name**: Account display name
    - **user_password**: Password (minimum 6 characters)

    After successful registration, you will receive an access token to use for other APIs.
    """
    return auth_service.register_user(db, request)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate user and return access token",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Incorrect email or password",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect email or password"}
                }
            }
        }
    }
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.

    - **user_email**: Registered email
    - **user_password**: Account password

    Returns access token if login credentials are correct.
    """
    return auth_service.login_user(db, request)
