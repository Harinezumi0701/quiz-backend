# app/schemas/namespace.py
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from app.schemas.http_response import SuccessResponse


class NamespaceOut(BaseModel):
    """Schema for namespace information"""

    id: UUID = Field(
        ..., description="Namespace ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    name: str = Field(..., description="Namespace name", example="categories")
    description: Optional[str] = Field(
        None, description="Namespace description", example="Category management"
    )
    prefix: str = Field(
        ..., description="Namespace prefix", example="categories"
    )
    created_at: int | None = Field(
        None, description="Created at Unix timestamp", example=1704067200
    )
    updated_at: int | None = Field(
        None, description="Updated at Unix timestamp", example=1704067200
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "categories",
                "description": "Category management",
                "prefix": "categories",
                "created_at": 1704067200,
                "updated_at": 1704067200,
            }
        }


class NamespaceListResponse(SuccessResponse[List[NamespaceOut]]):
    """Response schema for list of namespaces"""

    pass


class NamespaceResponse(SuccessResponse[NamespaceOut]):
    """Response schema for single namespace"""

    pass


class NamespaceCreateRequest(BaseModel):
    """Request schema for creating a namespace"""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Namespace name", example="categories"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Namespace description", example="Category management"
    )
    prefix: str = Field(
        ..., min_length=1, max_length=100, description="Namespace prefix", example="categories"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "categories",
                "description": "Category management",
                "prefix": "categories",
            }
        }


class NamespaceUpdateRequest(BaseModel):
    """Request schema for updating a namespace"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Namespace name", example="categories"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Namespace description", example="Category management"
    )
    prefix: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Namespace prefix", example="categories"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "categories",
                "description": "Category management",
                "prefix": "categories",
            }
        }
