from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from app.schemas.http_response import SuccessResponse


class TestDetailOut(BaseModel):
    """Schema for test with full details"""

    id: UUID = Field(
        ..., description="Test ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    name: str = Field(..., description="Test name", example="DVA-C02_Day_1")
    category_id: UUID = Field(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    description: str | None = Field(
        None,
        description="Test description",
        example="AWS DVA-C02 certification practice test",
    )
    time_limit: int | None = Field(
        None, description="Time limit in seconds", example=3600, ge=1
    )
    question_count: int = Field(
        ..., description="Number of questions in test", example=50
    )
    created_at: int | None = Field(
        None, description="Created at Unix timestamp", example=1704067200
    )
    updated_at: int | None = Field(
        None, description="Updated at Unix timestamp", example=1704067200
    )

    class Config:
        from_attributes = True


class TestDetailResponse(SuccessResponse[TestDetailOut]):
    """Response schema for single test"""

    pass


class TestDetailListResponse(SuccessResponse[List[TestDetailOut]]):
    """Response schema for list of tests with details"""

    pass


class TestCreateRequest(BaseModel):
    """Request schema for creating a test"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Test name",
        example="DVA-C02_Day_1",
    )
    category_id: UUID = Field(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    description: str | None = Field(
        None,
        description="Test description",
        example="AWS DVA-C02 certification practice test",
    )
    time_limit: int | None = Field(
        None, description="Time limit in seconds", example=3600, ge=1
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "DVA-C02_Day_1",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "description": "AWS DVA-C02 certification practice test",
                "time_limit": 3600,
            }
        }


class TestUpdateRequest(BaseModel):
    """Request schema for updating a test"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Test name",
        example="DVA-C02_Day_1",
    )
    description: str | None = Field(
        None,
        description="Test description",
        example="AWS DVA-C02 certification practice test",
    )
    time_limit: int | None = Field(
        None, description="Time limit in seconds", example=3600, ge=1
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "DVA-C02_Day_1",
                "description": "AWS DVA-C02 certification practice test",
                "time_limit": 3600,
            }
        }
