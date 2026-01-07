# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema cho đăng ký người dùng mới"""
    user_email: EmailStr = Field(..., description="Email của người dùng", example="user@example.com")
    account_name: str = Field(..., min_length=1, max_length=100, description="Tên tài khoản", example="John Doe")
    user_password: str = Field(..., min_length=6, description="Mật khẩu (tối thiểu 6 ký tự)", example="password123")

    class Config:
        json_schema_extra = {
            "example": {
                "user_email": "user@example.com",
                "account_name": "John Doe",
                "user_password": "password123"
            }
        }


class LoginRequest(BaseModel):
    """Request schema cho đăng nhập"""
    user_email: EmailStr = Field(..., description="Email của người dùng", example="user@example.com")
    user_password: str = Field(..., description="Mật khẩu", example="password123")

    class Config:
        json_schema_extra = {
            "example": {
                "user_email": "user@example.com",
                "user_password": "password123"
            }
        }


class TokenResponse(BaseModel):
    """Response schema cho access token"""
    access_token: str = Field(..., description="JWT access token", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", description="Loại token", example="bearer")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNjE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """Token data schema"""
    user_email: str | None = Field(None, description="Email từ token")
