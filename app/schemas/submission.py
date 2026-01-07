# app/schemas/submission.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class SubmissionCreate(BaseModel):
    """Schema for creating a submission"""
    question_id: int = Field(..., description="Question ID", example=1)
    selected_option_id: int = Field(..., description="Selected answer option ID", example=3)
    is_correct: bool = Field(..., description="Whether the submission is correct", example=True)

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": 1,
                "selected_option_id": 3,
                "is_correct": True
            }
        }


class SubmissionBulkCreate(BaseModel):
    """Schema for creating multiple submissions at once"""
    submissions: List[SubmissionCreate] = Field(..., description="List of submissions", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "submissions": [
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


class SubmissionOut(BaseModel):
    """Schema for saved submission"""
    id: int = Field(..., description="Submission ID", example=1)
    user_id: int = Field(..., description="User ID", example=1)
    question_id: int = Field(..., description="Question ID", example=1)
    selected_option_id: int = Field(..., description="Selected answer option ID", example=3)
    is_correct: bool = Field(..., description="Whether the submission is correct", example=True)
    answered_at: datetime | None = Field(None, description="Submission timestamp", example="2024-01-01T12:00:00")

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
    total_submitted: int = Field(..., description="Total submissions", example=50)
    correct_answers: int = Field(..., description="Number of correct answers", example=40)
    correct_submissions: int = Field(..., description="Number of correct submissions", example=40)
    wrong_answers: int = Field(..., description="Number of wrong answers", example=10)
    wrong_submissions: int = Field(..., description="Number of wrong submissions", example=10)
    accuracy: float = Field(..., description="Accuracy rate", example=0.8)
    last_attempt: str | None = Field(None, description="Last attempt", example="2024-01-01")


class RecentActivity(BaseModel):
    """Schema for recent activity"""
    id: int = Field(..., description="Submission ID", example=1)
    category: str = Field(..., description="Question category", example="DVA-C02")
    question_preview: str = Field(..., description="Question content preview", example="What is AWS Lambda?")
    is_correct: bool = Field(..., description="Whether the submission is correct", example=True)
    answered_at: str | None = Field(None, description="Submission timestamp", example="2024-01-01T12:00:00")


class OverallStatistics(BaseModel):
    """Schema for overall statistics"""
    total_answered: int = Field(..., description="Total questions answered", example=150)
    total_submitted: int = Field(..., description="Total submissions", example=150)
    total_correct: int = Field(..., description="Total correct submissions", example=120)
    total_wrong: int = Field(..., description="Total wrong submissions", example=30)
    overall_accuracy: float = Field(..., description="Overall accuracy rate", example=0.8)


class DashboardData(BaseModel):
    """Schema for dashboard data"""
    overall: OverallStatistics = Field(..., description="Overall statistics")
    by_category: List[CategoryStatistics] = Field(..., description="Statistics by category")
    recent_activity: List[RecentActivity] = Field(..., description="Recent activity")

