# app/schemas/submission.py
from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from app.schemas.http_response import SuccessResponse


class SubmissionCreate(BaseModel):
    """Schema for creating a submission"""
    question_id: UUID = Field(..., description="Question ID", example="550e8400-e29b-41d4-a716-446655440000")
    answer_id: UUID = Field(..., description="Selected answer option ID", example="550e8400-e29b-41d4-a716-446655440001")
    is_correct: bool = Field(..., description="Whether the submission is correct", example=True)

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "answer_id": "550e8400-e29b-41d4-a716-446655440001",
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
                        "question_id": "550e8400-e29b-41d4-a716-446655440000",
                        "answer_id": "550e8400-e29b-41d4-a716-446655440001",
                        "is_correct": True
                    },
                    {
                        "question_id": "550e8400-e29b-41d4-a716-446655440002",
                        "answer_id": "550e8400-e29b-41d4-a716-446655440003",
                        "is_correct": False
                    }
                ]
            }
        }


class SubmissionOut(BaseModel):
    """Schema for saved submission"""
    id: UUID = Field(..., description="Submission ID", example="550e8400-e29b-41d4-a716-446655440000")
    user_id: UUID = Field(..., description="User ID", example="550e8400-e29b-41d4-a716-446655440001")
    question_id: UUID = Field(..., description="Question ID", example="550e8400-e29b-41d4-a716-446655440002")
    answer_id: UUID = Field(..., description="Selected answer option ID", example="550e8400-e29b-41d4-a716-446655440003")
    is_correct: bool = Field(..., description="Whether the submission is correct", example=True)
    answered_at: int | None = Field(None, description="Submission Unix timestamp", example=1704067200)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "question_id": "550e8400-e29b-41d4-a716-446655440002",
                "answer_id": "550e8400-e29b-41d4-a716-446655440003",
                "is_correct": True,
                "answered_at": 1704067200
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
    last_attempt: int | None = Field(None, description="Last attempt Unix timestamp", example=1704067200)


class TestStatistics(BaseModel):
    """Schema for statistics by test"""
    test_id: str | None = Field(None, description="Test ID", example="550e8400-e29b-41d4-a716-446655440000")
    test_name: str = Field(..., description="Test name", example="Practice Test 1")
    total_answered: int = Field(..., description="Total questions answered", example=30)
    total_submitted: int = Field(..., description="Total submissions", example=30)
    correct_answers: int = Field(..., description="Number of correct answers", example=25)
    correct_submissions: int = Field(..., description="Number of correct submissions", example=25)
    wrong_answers: int = Field(..., description="Number of wrong answers", example=5)
    wrong_submissions: int = Field(..., description="Number of wrong submissions", example=5)
    accuracy: float = Field(..., description="Accuracy rate", example=83.3)
    last_attempt: int | None = Field(None, description="Last attempt Unix timestamp", example=1704067200)


class RecentActivity(BaseModel):
    """Schema for recent activity"""
    id: UUID = Field(..., description="Submission ID", example="550e8400-e29b-41d4-a716-446655440000")
    category: str = Field(..., description="Question category", example="DVA-C02")
    test_name: str = Field(..., description="Test name", example="Practice Test 1")
    question_preview: str = Field(..., description="Question content preview", example="What is AWS Lambda?")
    is_correct: bool = Field(..., description="Whether the submission is correct", example=True)
    answered_at: int | None = Field(None, description="Submission Unix timestamp", example=1704067200)


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
    by_test: dict[str, List[TestStatistics]] = Field(..., description="Statistics by test grouped by category")
    recent_activity: List[RecentActivity] = Field(..., description="Recent activity")


class SubmissionResponse(SuccessResponse[SubmissionOut]):
    """Response schema for single submission"""
    pass


class SubmissionListResponse(SuccessResponse[List[SubmissionOut]]):
    """Response schema for list of submissions"""
    pass


class DashboardResponse(SuccessResponse[DashboardData]):
    """Response schema for dashboard data"""
    pass

