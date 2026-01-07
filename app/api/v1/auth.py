# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, TokenData
from app.schemas.http_response import ErrorResponse
from app.services import auth_service
from app.db.session import get_db
from app.utils.response import success_response

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

    - **user_email**: User email (must be a valid email)
    - **account_name**: Account display name
    - **user_password**: Password (minimum 6 characters)

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

    - **user_email**: Registered email
    - **user_password**: Account password

    Returns access token if login credentials are correct.
    """
    token_data = auth_service.login_user(db, request)
    return TokenResponse(data=token_data, meta={})
