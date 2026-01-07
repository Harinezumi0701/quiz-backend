# app/api/v1/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services import auth_service
from app.db.session import get_db
from app.constants import HTTP_STATUS_CREATED

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=HTTP_STATUS_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.

    Returns an access token upon successful registration.
    """
    return auth_service.register_user(db, request)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.

    Returns an access token upon successful authentication.
    """
    return auth_service.login_user(db, request)
