# app/schemas/user.py
from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.constants.permissions import (
    PERMISSION_ACTION_READ,
    PERMISSION_NAMESPACE_CATEGORIES,
    PERMISSION_WILDCARD_ALL,
)
from app.schemas.http_response import SuccessResponse


class UserOut(BaseModel):
    """Schema for user information"""

    id: UUID = Field(
        ..., description="User ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    user_id: str = Field(
        ..., description="User ID (editable unique identifier)", example="abc123"
    )
    email: str = Field(..., description="User email", example="user@example.com")
    full_name: str = Field(..., description="Full name", example="John Doe")
    phone: str | None = Field(
        None, description="Phone number", example="+84123456789"
    )
    birthday: date | None = Field(None, description="Birthday", example="1990-01-01")
    address: str | None = Field(
        None, description="Address", example="123 Main St, City"
    )
    job_title: str | None = Field(
        None, description="Job title", example="Software Engineer"
    )
    company: str | None = Field(None, description="Company", example="Tech Corp")
    join_date: date | None = Field(
        None, description="Join date", example="2024-01-01"
    )
    role_id: UUID | None = Field(
        None, description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    role_name: str | None = Field(
        None, description="Role name", example="user"
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="List of user permissions",
        example=[
            f"{PERMISSION_NAMESPACE_CATEGORIES}::{PERMISSION_ACTION_READ}",
            PERMISSION_WILDCARD_ALL,
        ],
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "my_custom_user_id",
                "email": "user@example.com",
                "full_name": "John Doe",
                "phone": "+84123456789",
                "birthday": "1990-01-01",
                "address": "123 Main St, City",
                "job_title": "Software Engineer",
                "company": "Tech Corp",
                "join_date": "2024-01-01",
                "role_id": "550e8400-e29b-41d4-a716-446655440000",
                "permissions": [
                    f"{PERMISSION_NAMESPACE_CATEGORIES}::{PERMISSION_ACTION_READ}",
                    PERMISSION_WILDCARD_ALL,
                ],
            }
        }


class UserListResponse(SuccessResponse[list[UserOut]]):
    """Response schema for list of users"""

    pass


class UserResponse(SuccessResponse[UserOut]):
    """Response schema for single user"""

    pass


class UserCreateRequest(BaseModel):
    """Request schema for creating a new user"""

    email: EmailStr = Field(..., description="User email", example="user@example.com")
    full_name: str = Field(
        ..., min_length=1, max_length=255, description="Full name", example="John Doe"
    )
    user_id: str | None = Field(
        None,
        min_length=1,
        max_length=125,
        description="User ID (editable unique identifier matching [A-Za-z\\._-], 1-125 characters). If not provided, will be auto-generated.",
        example="abc123",
    )
    role_id: UUID | None = Field(
        None, description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    phone: str | None = Field(
        None, max_length=20, description="Phone number", example="+84123456789"
    )
    birthday: date | None = Field(None, description="Birthday", example="1990-01-01")
    address: str | None = Field(
        None, max_length=500, description="Address", example="123 Main St, City"
    )
    job_title: str | None = Field(
        None, max_length=100, description="Job title", example="Software Engineer"
    )
    company: str | None = Field(
        None, max_length=100, description="Company", example="Tech Corp"
    )
    join_date: date | None = Field(
        None, description="Join date", example="2024-01-01"
    )

    @field_validator("birthday", "join_date", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "user_id": "abc123",
                "role_id": "550e8400-e29b-41d4-a716-446655440000",
                "phone": "+84123456789",
                "birthday": "1990-01-01",
                "address": "123 Main St, City",
                "job_title": "Software Engineer",
                "company": "Tech Corp",
                "join_date": "2024-01-01",
            }
        }


class UserUpdateRequest(BaseModel):
    """Request schema for updating user information"""

    user_id: str | None = Field(
        None,
        min_length=1,
        max_length=125,
        description="User ID (editable unique identifier matching [A-Za-z\\._-], 1-125 characters)",
        example="abc123",
    )
    full_name: str | None = Field(
        None, min_length=1, max_length=255, description="Full name", example="John Doe"
    )
    phone: str | None = Field(
        None, max_length=20, description="Phone number", example="+84123456789"
    )
    birthday: date | None = Field(None, description="Birthday", example="1990-01-01")
    address: str | None = Field(
        None, max_length=500, description="Address", example="123 Main St, City"
    )
    job_title: str | None = Field(
        None, max_length=100, description="Job title", example="Software Engineer"
    )
    company: str | None = Field(
        None, max_length=100, description="Company", example="Tech Corp"
    )
    join_date: date | None = Field(
        None, description="Join date", example="2024-01-01"
    )
    role_id: UUID | None = Field(
        None, description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    )

    @field_validator("birthday", "join_date", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "my_custom_user_id",
                "full_name": "John Doe",
                "phone": "+84123456789",
                "birthday": "1990-01-01",
                "address": "123 Main St, City",
                "job_title": "Software Engineer",
                "company": "Tech Corp",
                "join_date": "2024-01-01",
            }
        }


class ChangePasswordRequest(BaseModel):
    """Request schema for changing user password"""

    current_password: str = Field(
        ..., min_length=1, description="Current password", example="currentpassword123"
    )
    new_password: str = Field(
        ...,
        min_length=6,
        description="New password (minimum 6 characters)",
        example="newpassword123",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "currentpassword123",
                "new_password": "newpassword123",
            }
        }


class AdminChangePasswordRequest(BaseModel):
    """Request schema for admin to change user password"""

    new_password: str = Field(
        ...,
        min_length=6,
        description="New password (minimum 6 characters)",
        example="newpassword123",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "new_password": "newpassword123",
            }
        }


class AssignRoleRequest(BaseModel):
    """Request schema for assigning role to user"""

    role_id: UUID = Field(
        ..., description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "role_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
