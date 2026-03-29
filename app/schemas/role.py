# app/schemas/role.py
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


class RoleOut(BaseModel):
    """Schema for role information"""

    id: UUID = Field(
        ..., description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    name: str = Field(..., description="Role name", example="admin")
    description: str | None = Field(
        None,
        description="Role description",
        example="Administrator with full permissions",
    )
    default: bool = Field(
        default=False,
        description="Whether this is the default role for new users",
        example=False,
    )
    permissions: list[PermissionOut] = Field(
        default_factory=list, description="List of permissions for this role"
    )
    created_at: datetime = Field(..., description="Created at timestamp")
    updated_at: datetime = Field(..., description="Updated at timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "admin",
                "description": "Administrator with full permissions",
                "default": False,
                "permissions": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "permission": "*::*",
                        "created_at": "2025-01-17T10:00:00Z",
                    }
                ],
                "created_at": "2025-01-17T10:00:00Z",
                "updated_at": "2025-01-17T10:00:00Z",
            }
        }


class RoleListResponse(SuccessResponse[list[RoleOut]]):
    """Response schema for list of roles"""

    pass


class RoleResponse(SuccessResponse[RoleOut]):
    """Response schema for single role"""

    pass


class RoleCreateRequest(BaseModel):
    """Request schema for creating a role"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Role name",
        example="admin",
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Role description",
        example="Administrator with full permissions",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "admin",
                "description": "Administrator with full permissions",
            }
        }


class RoleUpdateRequest(BaseModel):
    """Request schema for updating a role"""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Role name",
        example="admin",
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Role description",
        example="Administrator with full permissions",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "admin",
                "description": "Administrator with full permissions",
            }
        }
