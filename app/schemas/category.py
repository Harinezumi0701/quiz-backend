from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.http_response import SuccessResponse


class CategoryDetailOut(BaseModel):
    """Schema for category with ID"""
    id: UUID = Field(..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000")
    name: str = Field(..., description="Category name", example="DVA-C02")
    question_count: int = Field(..., description="Number of questions in category", example=150)
    created_at: int | None = Field(None, description="Created at Unix timestamp", example=1704067200)
    updated_at: int | None = Field(None, description="Updated at Unix timestamp", example=1704067200)

    class Config:
        from_attributes = True


class CategoryDetailResponse(SuccessResponse[CategoryDetailOut]):
    """Response schema for single category"""
    pass


class CategoryDetailListResponse(SuccessResponse[list[CategoryDetailOut]]):
    """Response schema for list of categories with details"""
    pass


class CategoryCreateRequest(BaseModel):
    """Request schema for creating a category"""
    name: str = Field(..., min_length=1, max_length=100, description="Category name", example="DVA-C02")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "DVA-C02"
            }
        }


class CategoryUpdateRequest(BaseModel):
    """Request schema for updating a category"""
    name: str = Field(..., min_length=1, max_length=100, description="Category name", example="DVA-C02")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "DVA-C02"
            }
        }
