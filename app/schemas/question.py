from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from app.schemas.http_response import SuccessResponse


class CategoryOut(BaseModel):
    """Schema for question category"""
    category: str = Field(..., description="Category name", example="DVA-C02")
    question_count: int = Field(..., description="Number of questions in category", example=150)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "category": "DVA-C02",
                "question_count": 150
            }
        }


class QuestionSetOut(BaseModel):
    """Schema for a question set/dump in a category"""
    question_set: str = Field(..., description="Question set name", example="DVA-C02_Day_1")
    question_count: int = Field(..., description="Number of questions in set", example=50)
    question_range: str = Field(..., description="Question range", example="1-50")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "question_set": "DVA-C02_Day_1",
                "question_count": 50,
                "question_range": "1-50"
            }
        }


class CategoryWithSetsOut(BaseModel):
    """Schema for category with all question sets"""
    category: str = Field(..., description="Category name", example="DVA-C02")
    total_questions: int = Field(..., description="Total number of questions in category", example=150)
    question_sets: List[QuestionSetOut] = Field(..., description="List of question sets")

    class Config:
        from_attributes = True


class AnswerOut(BaseModel):
    """Schema for answer"""
    id: UUID = Field(..., description="Answer ID", example="550e8400-e29b-41d4-a716-446655440000")
    content: str = Field(..., description="Answer content", example="Option A")
    is_correct: bool = Field(..., description="Whether this is the correct answer", example=True)
    explanation: str | None = Field(None, description="Explanation for the answer", example="This is the correct answer because...")

    class Config:
        from_attributes = True


class QuestionWithAnswers(BaseModel):
    """Schema for question with answers"""
    id: UUID = Field(..., description="Question ID", example="550e8400-e29b-41d4-a716-446655440000")
    content: str = Field(..., description="Question content", example="What is AWS Lambda?")
    image_url: str | None = Field(None, description="Image URL (if available)", example="https://example.com/image.png")
    category: str | None = Field(None, description="Question category", example="DVA-C02")
    question_set: str | None = Field(None, description="Question set", example="DVA-C02_Day_1")
    created_at: int | None = Field(None, description="Created at Unix timestamp", example=1704067200)
    updated_at: int | None = Field(None, description="Updated at Unix timestamp", example=1704067200)
    answers: List[AnswerOut] = Field(..., description="List of answers")

    class Config:
        from_attributes = True


class QuestionOut(BaseModel):
    """Schema for question (without answers)"""
    id: UUID = Field(..., description="Question ID", example="550e8400-e29b-41d4-a716-446655440000")
    content: str = Field(..., description="Question content", example="What is AWS Lambda?")
    image_url: str | None = Field(None, description="Image URL (if available)")
    category: str | None = Field(None, description="Question category", example="DVA-C02")

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


class CategoryListResponse(SuccessResponse[List[CategoryOut]]):
    """Response schema for list of categories"""
    pass


class CategoryDetailResponse(SuccessResponse[CategoryDetailOut]):
    """Response schema for single category"""
    pass


class CategoryDetailListResponse(SuccessResponse[List[CategoryDetailOut]]):
    """Response schema for list of categories with details"""
    pass


class CategoryWithSetsListResponse(SuccessResponse[List[CategoryWithSetsOut]]):
    """Response schema for list of categories with sets"""
    pass


class QuestionListResponse(SuccessResponse[List[QuestionWithAnswers]]):
    """Response schema for list of questions with answers"""
    pass


class QuestionResponse(SuccessResponse[QuestionWithAnswers]):
    """Response schema for single question"""
    pass
