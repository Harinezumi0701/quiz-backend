# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID
from datetime import date
from app.schemas.http_response import SuccessResponse
from app.schemas.role import PermissionOut
from app.constants.permissions import (
    PERMISSION_NAMESPACE_CATEGORIES,
    PERMISSION_ACTION_READ,
    PERMISSION_WILDCARD_ALL,
)


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
    phone: Optional[str] = Field(
        None, description="Phone number", example="+84123456789"
    )
    birthday: Optional[date] = Field(None, description="Birthday", example="1990-01-01")
    address: Optional[str] = Field(
        None, description="Address", example="123 Main St, City"
    )
    job_title: Optional[str] = Field(
        None, description="Job title", example="Software Engineer"
    )
    company: Optional[str] = Field(None, description="Company", example="Tech Corp")
    join_date: Optional[date] = Field(
        None, description="Join date", example="2024-01-01"
    )
    role_id: Optional[UUID] = Field(
        None, description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    permissions: List[str] = Field(
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


class UserListResponse(SuccessResponse[List[UserOut]]):
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
    user_id: Optional[str] = Field(
        None,
        min_length=1,
        max_length=125,
        description="User ID (editable unique identifier matching [A-Za-z\\._-], 1-125 characters). If not provided, will be auto-generated.",
        example="abc123",
    )
    role_id: Optional[UUID] = Field(
        None, description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    phone: Optional[str] = Field(
        None, max_length=20, description="Phone number", example="+84123456789"
    )
    birthday: Optional[date] = Field(None, description="Birthday", example="1990-01-01")
    address: Optional[str] = Field(
        None, max_length=500, description="Address", example="123 Main St, City"
    )
    job_title: Optional[str] = Field(
        None, max_length=100, description="Job title", example="Software Engineer"
    )
    company: Optional[str] = Field(
        None, max_length=100, description="Company", example="Tech Corp"
    )
    join_date: Optional[date] = Field(
        None, description="Join date", example="2024-01-01"
    )

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

    user_id: Optional[str] = Field(
        None,
        min_length=1,
        max_length=125,
        description="User ID (editable unique identifier matching [A-Za-z\\._-], 1-125 characters)",
        example="abc123",
    )
    full_name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Full name", example="John Doe"
    )
    phone: Optional[str] = Field(
        None, max_length=20, description="Phone number", example="+84123456789"
    )
    birthday: Optional[date] = Field(None, description="Birthday", example="1990-01-01")
    address: Optional[str] = Field(
        None, max_length=500, description="Address", example="123 Main St, City"
    )
    job_title: Optional[str] = Field(
        None, max_length=100, description="Job title", example="Software Engineer"
    )
    company: Optional[str] = Field(
        None, max_length=100, description="Company", example="Tech Corp"
    )
    join_date: Optional[date] = Field(
        None, description="Join date", example="2024-01-01"
    )
    role_id: Optional[UUID] = Field(
        None, description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    )

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
