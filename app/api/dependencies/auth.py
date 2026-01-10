# app/api/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.security import decode_access_token
from app.services import auth_service
from app.models.users import User
from app.constants import (
    ERROR_COULD_NOT_VALIDATE_CREDENTIALS,
    ERROR_USER_NOT_FOUND,
    JWT_TOKEN_TYPE,
)

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user.

    Extracts and validates the JWT token from the Authorization header.
    Returns the User object if authentication is successful.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    token = credentials.credentials

    # Decode the token
    email = decode_access_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_COULD_NOT_VALIDATE_CREDENTIALS,
            headers={"WWW-Authenticate": JWT_TOKEN_TYPE},
        )

    # Get the user from database
    user = auth_service.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_USER_NOT_FOUND,
            headers={"WWW-Authenticate": JWT_TOKEN_TYPE},
        )

    return user
