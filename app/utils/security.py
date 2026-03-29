# app/utils/security.py
import os
from datetime import UTC, datetime, timedelta

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.constants import (
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
    DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
    DEFAULT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_SUBJECT_KEY,
    PASSWORD_SCHEME,
)

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=[PASSWORD_SCHEME], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
ALGORITHM = os.getenv("ALGORITHM", JWT_ALGORITHM)
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES)))
REFRESH_TOKEN_EXPIRE_DAYS = float(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", str(DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS)))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> str | None:
    """Decode and verify a JWT token, returning the user email."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get(JWT_SUBJECT_KEY)
        if email is None:
            return None
        return email
    except JWTError:
        return None


def create_refresh_token() -> str:
    """Create a random refresh token string."""
    import secrets
    return secrets.token_urlsafe(32)


def get_refresh_token_expires_delta() -> timedelta:
    """Get the expiration time delta for refresh tokens."""
    return timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
