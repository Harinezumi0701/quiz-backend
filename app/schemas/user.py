# app/schemas/user.py
from pydantic import BaseModel, Field
from typing import List
from app.schemas.http_response import SuccessResponse


class UserOut(BaseModel):
    """Schema for user information"""
    id: int = Field(..., description="User ID", example=1)
    account_name: str = Field(..., description="Account name", example="John Doe")
    user_email: str = Field(..., description="User email", example="user@example.com")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "account_name": "John Doe",
                "user_email": "user@example.com"
            }
        }


class UserListResponse(SuccessResponse[List[UserOut]]):
    """Response schema for list of users"""
    pass


class UserResponse(SuccessResponse[UserOut]):
    """Response schema for single user"""
    pass
