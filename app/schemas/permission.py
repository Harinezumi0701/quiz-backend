# app/schemas/permission.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.constants.permissions import (
    PERMISSION_ACTION_READ,
    PERMISSION_NAMESPACE_CATEGORIES,
)
from app.schemas.http_response import SuccessResponse


class PermissionOut(BaseModel):
    """Schema for permission information"""

    id: UUID = Field(
        ..., description="Permission ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    role_id: UUID = Field(
        ..., description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    permission: str = Field(
        ...,
        description="Permission string",
        example=f"{PERMISSION_NAMESPACE_CATEGORIES}::{PERMISSION_ACTION_READ}",
    )
    name: str | None = Field(
        None, description="Permission name", example="Read Categories"
    )
    description: str | None = Field(
        None, description="Permission description", example="Allow reading category information"
    )
    created_at: datetime = Field(..., description="Created at timestamp")

    class Config:
        from_attributes = True


class PermissionListResponse(SuccessResponse[list[PermissionOut]]):
    """Response schema for list of permissions"""

    pass


class PermissionResponse(SuccessResponse[PermissionOut]):
    """Response schema for single permission"""

    pass


class PermissionCreateRequest(BaseModel):
    """Request schema for creating a permission"""

    role_id: UUID = Field(
        ..., description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    permission: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Permission string (format: namespace::action or *::*)",
        example=f"{PERMISSION_NAMESPACE_CATEGORIES}::{PERMISSION_ACTION_READ}",
    )
    name: str | None = Field(
        None, max_length=200, description="Permission name", example="Read Categories"
    )
    description: str | None = Field(
        None, max_length=500, description="Permission description", example="Allow reading category information"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "role_id": "550e8400-e29b-41d4-a716-446655440000",
                "permission": f"{PERMISSION_NAMESPACE_CATEGORIES}::{PERMISSION_ACTION_READ}",
                "name": "Read Categories",
                "description": "Allow reading category information",
            }
        }


class PermissionUpdateRequest(BaseModel):
    """Request schema for updating a permission"""

    role_id: UUID | None = Field(
        None, description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    permission: str | None = Field(
        None,
        min_length=1,
        max_length=200,
        description="Permission string (format: namespace::action or *::*)",
        example=f"{PERMISSION_NAMESPACE_CATEGORIES}::{PERMISSION_ACTION_READ}",
    )
    name: str | None = Field(
        None, max_length=200, description="Permission name", example="Read Categories"
    )
    description: str | None = Field(
        None, max_length=500, description="Permission description", example="Allow reading category information"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "role_id": "550e8400-e29b-41d4-a716-446655440000",
                "permission": f"{PERMISSION_NAMESPACE_CATEGORIES}::{PERMISSION_ACTION_READ}",
                "name": "Read Categories",
                "description": "Allow reading category information",
            }
        }
