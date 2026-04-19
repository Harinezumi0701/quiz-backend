from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from app.schemas.http_response import SuccessResponse
from app.schemas.answer import AnswerOut


class Question(BaseModel):
    """Schema for question without answers"""
    id: UUID = Field(..., description="Question ID", example="550e8400-e29b-41d4-a716-446655440000")
    content: str = Field(..., description="Question content", example="What is AWS Lambda?")
    image_url: str | None = Field(None, description="Image URL (if available)", example="https://example.com/image.png")
    category: str | None = Field(None, description="Question category", example="DVA-C02")
    test: str | None = Field(None, description="Test", example="DVA-C02_Day_1")
    is_multiple_choice: bool = Field(False, description="Whether this question has multiple correct answers", example=False)
    created_at: int | None = Field(None, description="Created at Unix timestamp", example=1704067200)
    answer_count: int = Field(..., description="Number of answers for this question", example=4)

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


class QuestionListResponse(SuccessResponse[List[Question]]):
    """Response schema for list of questions"""
    pass


class QuestionWithAnswersListResponse(SuccessResponse[List[QuestionWithAnswers]]):
    """Response schema for list of questions with full answer details"""
    pass


class QuestionResponse(SuccessResponse[QuestionWithAnswers]):
    """Response schema for single question"""
    pass


class QuestionCreateRequest(BaseModel):
    """Request schema for creating a question"""
    content: str = Field(..., min_length=1, description="Question content", example="What is AWS Lambda?")
    image_url: str | None = Field(None, description="Image URL (if available)", example="https://example.com/image.png")
    category_id: UUID | None = Field(None, description="Category ID", example="550e8400-e29b-41d4-a716-446655440000")
    test_id: UUID | None = Field(None, description="Test ID", example="550e8400-e29b-41d4-a716-446655440000")
    is_multiple_choice: bool = Field(False, description="Whether this question has multiple correct answers", example=False)

    class Config:
        json_schema_extra = {
            "example": {
                "content": "What is AWS Lambda?",
                "image_url": "https://example.com/image.png",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "test_id": "550e8400-e29b-41d4-a716-446655440000",
                "is_multiple_choice": False
            }
        }


class QuestionUpdateRequest(BaseModel):
    """Request schema for updating a question"""
    content: str | None = Field(None, min_length=1, description="Question content", example="What is AWS Lambda?")
    image_url: str | None = Field(None, description="Image URL (if available)", example="https://example.com/image.png")
    category_id: UUID | None = Field(None, description="Category ID", example="550e8400-e29b-41d4-a716-446655440000")
    test_id: UUID | None = Field(None, description="Test ID", example="550e8400-e29b-41d4-a716-446655440000")
    is_multiple_choice: bool | None = Field(None, description="Whether this question has multiple correct answers", example=False)

    class Config:
        json_schema_extra = {
            "example": {
                "content": "What is AWS Lambda?",
                "image_url": "https://example.com/image.png",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "test_id": "550e8400-e29b-41d4-a716-446655440000",
                "is_multiple_choice": False
            }
        }
