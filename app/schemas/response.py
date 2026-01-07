# app/schemas/response.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class ResponseCreate(BaseModel):
    """Schema cho việc tạo một câu trả lời"""
    question_id: int = Field(..., description="ID của câu hỏi", example=1)
    selected_option_id: int = Field(..., description="ID của đáp án được chọn", example=3)
    is_correct: bool = Field(..., description="Có phải đáp án đúng không", example=True)

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": 1,
                "selected_option_id": 3,
                "is_correct": True
            }
        }


class ResponseBulkCreate(BaseModel):
    """Schema cho việc tạo nhiều câu trả lời cùng lúc"""
    responses: List[ResponseCreate] = Field(..., description="Danh sách các câu trả lời", min_length=1)

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
    """Schema cho câu trả lời đã được lưu"""
    id: int = Field(..., description="ID của response", example=1)
    user_id: int = Field(..., description="ID của người dùng", example=1)
    question_id: int = Field(..., description="ID của câu hỏi", example=1)
    selected_option_id: int = Field(..., description="ID của đáp án được chọn", example=3)
    is_correct: bool = Field(..., description="Có phải đáp án đúng không", example=True)
    answered_at: datetime | None = Field(None, description="Thời gian trả lời", example="2024-01-01T12:00:00")

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
    """Schema cho thống kê theo danh mục"""
    category: str = Field(..., description="Tên danh mục", example="DVA-C02")
    total_answered: int = Field(..., description="Tổng số câu đã trả lời", example=50)
    correct_answers: int = Field(..., description="Số câu trả lời đúng", example=40)
    wrong_answers: int = Field(..., description="Số câu trả lời sai", example=10)
    accuracy: float = Field(..., description="Tỷ lệ chính xác", example=0.8)
    last_attempt: str | None = Field(None, description="Lần thử cuối cùng", example="2024-01-01")


class RecentActivity(BaseModel):
    """Schema cho hoạt động gần đây"""
    id: int = Field(..., description="ID của response", example=1)
    category: str = Field(..., description="Danh mục câu hỏi", example="DVA-C02")
    question_preview: str = Field(..., description="Xem trước nội dung câu hỏi", example="What is AWS Lambda?")
    is_correct: bool = Field(..., description="Có phải đáp án đúng không", example=True)
    answered_at: str | None = Field(None, description="Thời gian trả lời", example="2024-01-01T12:00:00")


class OverallStatistics(BaseModel):
    """Schema cho thống kê tổng quan"""
    total_answered: int = Field(..., description="Tổng số câu đã trả lời", example=150)
    total_correct: int = Field(..., description="Tổng số câu trả lời đúng", example=120)
    total_wrong: int = Field(..., description="Tổng số câu trả lời sai", example=30)
    overall_accuracy: float = Field(..., description="Tỷ lệ chính xác tổng thể", example=0.8)


class DashboardData(BaseModel):
    """Schema cho dữ liệu dashboard"""
    overall: OverallStatistics = Field(..., description="Thống kê tổng quan")
    by_category: List[CategoryStatistics] = Field(..., description="Thống kê theo danh mục")
    recent_activity: List[RecentActivity] = Field(..., description="Hoạt động gần đây")
