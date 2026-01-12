from pydantic import BaseModel, Field
from uuid import UUID
from app.schemas.http_response import SuccessResponse


class AnswerOut(BaseModel):
    """Schema for answer"""
    id: UUID = Field(..., description="Answer ID", example="550e8400-e29b-41d4-a716-446655440000")
    question_id: UUID | None = Field(None, description="Question ID", example="550e8400-e29b-41d4-a716-446655440000")
    content: str | None = Field(None, description="Answer content", example="Option A")
    image_url: str | None = Field(None, description="Image URL (if available)", example="https://example.com/image.png")
    is_correct: bool = Field(..., description="Whether this is the correct answer", example=True)
    explanation: str | None = Field(None, description="Explanation for the answer", example="This is the correct answer because...")
    created_at: int | None = Field(None, description="Created at Unix timestamp", example=1704067200)
    updated_at: int | None = Field(None, description="Updated at Unix timestamp", example=1704067200)

    class Config:
        from_attributes = True


class AnswerListResponse(SuccessResponse[list[AnswerOut]]):
    """Response schema for list of answers"""
    pass


class AnswerResponse(SuccessResponse[AnswerOut]):
    """Response schema for single answer"""
    pass


class AnswerCreateRequest(BaseModel):
    """Request schema for creating an answer"""
    question_id: UUID = Field(..., description="Question ID", example="550e8400-e29b-41d4-a716-446655440000")
    content: str | None = Field(None, description="Answer content", example="Option A")
    image_url: str | None = Field(None, description="Image URL (if available)", example="https://example.com/image.png")
    is_correct: bool = Field(False, description="Whether this is the correct answer", example=True)
    explanation: str | None = Field(None, description="Explanation for the answer", example="This is the correct answer because...")

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "content": "Option A",
                "image_url": "https://example.com/image.png",
                "is_correct": True,
                "explanation": "This is the correct answer because..."
            }
        }


class AnswerUpdateRequest(BaseModel):
    """Request schema for updating an answer"""
    content: str | None = Field(None, description="Answer content", example="Option A")
    image_url: str | None = Field(None, description="Image URL (if available)", example="https://example.com/image.png")
    is_correct: bool | None = Field(None, description="Whether this is the correct answer", example=True)
    explanation: str | None = Field(None, description="Explanation for the answer", example="This is the correct answer because...")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Option A",
                "image_url": "https://example.com/image.png",
                "is_correct": True,
                "explanation": "This is the correct answer because..."
            }
        }
