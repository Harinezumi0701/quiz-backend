from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from app.schemas.http_response import SuccessResponse


class TestDetailOut(BaseModel):
    """Schema for test with full details"""
    id: UUID = Field(..., description="Test ID", example="550e8400-e29b-41d4-a716-446655440000")
    name: str = Field(..., description="Test name", example="DVA-C02_Day_1")
    category_id: UUID = Field(..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000")
    question_count: int = Field(..., description="Number of questions in test", example=50)
    created_at: int | None = Field(None, description="Created at Unix timestamp", example=1704067200)
    updated_at: int | None = Field(None, description="Updated at Unix timestamp", example=1704067200)

    class Config:
        from_attributes = True


class AnswerOut(BaseModel):
    """Schema for answer"""
    id: UUID = Field(..., description="Answer ID", example="550e8400-e29b-41d4-a716-446655440000")
    question_id: UUID | None = Field(None, description="Question ID", example="550e8400-e29b-41d4-a716-446655440000")
    content: str = Field(..., description="Answer content", example="Option A")
    is_correct: bool = Field(..., description="Whether this is the correct answer", example=True)
    explanation: str | None = Field(None, description="Explanation for the answer", example="This is the correct answer because...")
    created_at: int | None = Field(None, description="Created at Unix timestamp", example=1704067200)
    updated_at: int | None = Field(None, description="Updated at Unix timestamp", example=1704067200)

    class Config:
        from_attributes = True


class QuestionWithAnswers(BaseModel):
    """Schema for question with answers"""
    id: UUID = Field(..., description="Question ID", example="550e8400-e29b-41d4-a716-446655440000")
    content: str = Field(..., description="Question content", example="What is AWS Lambda?")
    image_url: str | None = Field(None, description="Image URL (if available)", example="https://example.com/image.png")
    category: str | None = Field(None, description="Question category", example="DVA-C02")
    test: str | None = Field(None, description="Test", example="DVA-C02_Day_1")
    is_multiple_choice: bool = Field(False, description="Whether this question has multiple correct answers", example=False)
    created_at: int | None = Field(None, description="Created at Unix timestamp", example=1704067200)
    updated_at: int | None = Field(None, description="Updated at Unix timestamp", example=1704067200)
    answers: List[AnswerOut] = Field(..., description="List of answers")

    class Config:
        from_attributes = True


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


class CategoryDetailListResponse(SuccessResponse[List[CategoryDetailOut]]):
    """Response schema for list of categories with details"""
    pass


class QuestionListResponse(SuccessResponse[List[QuestionWithAnswers]]):
    """Response schema for list of questions with answers"""
    pass


class QuestionResponse(SuccessResponse[QuestionWithAnswers]):
    """Response schema for single question"""
    pass


class TestDetailListResponse(SuccessResponse[List[TestDetailOut]]):
    """Response schema for list of tests with details"""
    pass


class TestDetailResponse(SuccessResponse[TestDetailOut]):
    """Response schema for single test"""
    pass


class AnswerListResponse(SuccessResponse[List[AnswerOut]]):
    """Response schema for list of answers"""
    pass


class AnswerResponse(SuccessResponse[AnswerOut]):
    """Response schema for single answer"""
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
