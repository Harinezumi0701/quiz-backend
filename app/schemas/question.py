from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from app.schemas.http_response import SuccessResponse


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


class QuestionListResponse(SuccessResponse[List[QuestionWithAnswers]]):
    """Response schema for list of questions with answers"""
    pass


class QuestionResponse(SuccessResponse[QuestionWithAnswers]):
    """Response schema for single question"""
    pass


class AnswerListResponse(SuccessResponse[List[AnswerOut]]):
    """Response schema for list of answers"""
    pass


class AnswerResponse(SuccessResponse[AnswerOut]):
    """Response schema for single answer"""
    pass
