# app/schemas/response.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class ResponseCreate(BaseModel):
    """Schema for creating a response"""
    question_id: int = Field(..., description="Question ID", example=1)
    selected_option_id: int = Field(..., description="Selected answer option ID", example=3)
    is_correct: bool = Field(..., description="Whether the answer is correct", example=True)

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": 1,
                "selected_option_id": 3,
                "is_correct": True
            }
        }


class ResponseBulkCreate(BaseModel):
    """Schema for creating multiple responses at once"""
    responses: List[ResponseCreate] = Field(..., description="List of responses", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "responses": [
                    {
                        "question_id": 1,
                        "selected_option_id": 3,
                        "is_correct": True
                    },
                    {
                        "question_id": 2,
                        "selected_option_id": 5,
                        "is_correct": False
                    }
                ]
            }
        }


class ResponseOut(BaseModel):
    """Schema for saved response"""
    id: int = Field(..., description="Response ID", example=1)
    user_id: int = Field(..., description="User ID", example=1)
    question_id: int = Field(..., description="Question ID", example=1)
    selected_option_id: int = Field(..., description="Selected answer option ID", example=3)
    is_correct: bool = Field(..., description="Whether the answer is correct", example=True)
    answered_at: datetime | None = Field(None, description="Answer timestamp", example="2024-01-01T12:00:00")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "question_id": 1,
                "selected_option_id": 3,
                "is_correct": True,
                "answered_at": "2024-01-01T12:00:00"
            }
        }


class CategoryStatistics(BaseModel):
    """Schema for statistics by category"""
    category: str = Field(..., description="Category name", example="DVA-C02")
    total_answered: int = Field(..., description="Total questions answered", example=50)
    correct_answers: int = Field(..., description="Number of correct answers", example=40)
    wrong_answers: int = Field(..., description="Number of wrong answers", example=10)
    accuracy: float = Field(..., description="Accuracy rate", example=0.8)
    last_attempt: str | None = Field(None, description="Last attempt", example="2024-01-01")


class RecentActivity(BaseModel):
    """Schema for recent activity"""
    id: int = Field(..., description="Response ID", example=1)
    category: str = Field(..., description="Question category", example="DVA-C02")
    question_preview: str = Field(..., description="Question content preview", example="What is AWS Lambda?")
    is_correct: bool = Field(..., description="Whether the answer is correct", example=True)
    answered_at: str | None = Field(None, description="Answer timestamp", example="2024-01-01T12:00:00")


class OverallStatistics(BaseModel):
    """Schema for overall statistics"""
    total_answered: int = Field(..., description="Total questions answered", example=150)
    total_correct: int = Field(..., description="Total correct answers", example=120)
    total_wrong: int = Field(..., description="Total wrong answers", example=30)
    overall_accuracy: float = Field(..., description="Overall accuracy rate", example=0.8)


class DashboardData(BaseModel):
    """Schema for dashboard data"""
    overall: OverallStatistics = Field(..., description="Overall statistics")
    by_category: List[CategoryStatistics] = Field(..., description="Statistics by category")
    recent_activity: List[RecentActivity] = Field(..., description="Recent activity")
