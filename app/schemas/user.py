# app/schemas/user.py
from pydantic import BaseModel, Field


class UserOut(BaseModel):
    """Schema for user information"""
    id: int = Field(..., description="User ID", example=1)
    account_name: str = Field(..., description="Account name", example="John Doe")
    user_email: str = Field(..., description="User email", example="user@example.com")

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "account_name": "John Doe",
                "user_email": "user@example.com"
            }
        }
