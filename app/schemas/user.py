# app/schemas/user.py
from pydantic import BaseModel, Field


class UserOut(BaseModel):
    """Schema cho thông tin người dùng"""
    id: int = Field(..., description="ID của người dùng", example=1)
    account_name: str = Field(..., description="Tên tài khoản", example="John Doe")
    user_email: str = Field(..., description="Email của người dùng", example="user@example.com")

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "account_name": "John Doe",
                "user_email": "user@example.com"
            }
        }
