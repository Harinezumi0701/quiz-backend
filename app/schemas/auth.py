# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from app.schemas.http_response import SuccessResponse


class RegisterRequest(BaseModel):
    """Request schema for new user registration"""
    user_email: EmailStr = Field(..., description="User email", example="user@example.com")
    account_name: str = Field(..., min_length=1, max_length=100, description="Account name", example="John Doe")
    user_password: str = Field(..., min_length=6, description="Password (minimum 6 characters)", example="password123")

    class Config:
        json_schema_extra = {
            "example": {
                "user_email": "user@example.com",
                "account_name": "John Doe",
                "user_password": "password123"
            }
        }


class LoginRequest(BaseModel):
    """Request schema for login"""
    user_email: EmailStr = Field(..., description="User email", example="user@example.com")
    user_password: str = Field(..., description="Password", example="password123")

    class Config:
        json_schema_extra = {
            "example": {
                "user_email": "user@example.com",
                "user_password": "password123"
            }
        }


class TokenData(BaseModel):
    """Token data schema"""
    access_token: str = Field(..., description="JWT access token", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", description="Token type", example="bearer")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNjE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "token_type": "bearer"
            }
        }


class TokenResponse(SuccessResponse[TokenData]):
    """Response schema for access token wrapped in standard response"""
    pass


class TokenDataInternal(BaseModel):
    """Token data schema for internal use"""
    user_email: str | None = Field(None, description="Email from token")
