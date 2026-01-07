from pydantic import BaseModel, Field
from typing import List


class CategoryOut(BaseModel):
    """Schema cho danh mục câu hỏi"""
    category: str = Field(..., description="Tên danh mục", example="DVA-C02")
    question_count: int = Field(..., description="Số lượng câu hỏi trong danh mục", example=150)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "category": "DVA-C02",
                "question_count": 150
            }
        }


class QuestionSetOut(BaseModel):
    """Schema cho một set/dump câu hỏi trong danh mục"""
    question_set: str = Field(..., description="Tên của question set", example="DVA-C02_Day_1")
    question_count: int = Field(..., description="Số lượng câu hỏi trong set", example=50)
    question_range: str = Field(..., description="Khoảng câu hỏi", example="1-50")

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
    """Schema cho danh mục kèm tất cả các question sets"""
    category: str = Field(..., description="Tên danh mục", example="DVA-C02")
    total_questions: int = Field(..., description="Tổng số câu hỏi trong danh mục", example=150)
    question_sets: List[QuestionSetOut] = Field(..., description="Danh sách các question sets")

    class Config:
        from_attributes = True


class AnswerOut(BaseModel):
    """Schema cho câu trả lời"""
    id: int = Field(..., description="ID của câu trả lời", example=1)
    content: str = Field(..., description="Nội dung câu trả lời", example="Option A")
    is_correct: bool = Field(..., description="Có phải đáp án đúng không", example=True)
    explanation: str | None = Field(None, description="Giải thích cho câu trả lời", example="This is the correct answer because...")

    class Config:
        from_attributes = True


class QuestionWithAnswers(BaseModel):
    """Schema cho câu hỏi kèm các câu trả lời"""
    id: int = Field(..., description="ID của câu hỏi", example=1)
    content: str = Field(..., description="Nội dung câu hỏi", example="What is AWS Lambda?")
    image_url: str | None = Field(None, description="URL hình ảnh (nếu có)", example="https://example.com/image.png")
    category: str | None = Field(None, description="Danh mục câu hỏi", example="DVA-C02")
    answers: List[AnswerOut] = Field(..., description="Danh sách các câu trả lời")

    class Config:
        from_attributes = True


class QuestionOut(BaseModel):
    """Schema cho câu hỏi (không kèm câu trả lời)"""
    id: int = Field(..., description="ID của câu hỏi", example=1)
    content: str = Field(..., description="Nội dung câu hỏi", example="What is AWS Lambda?")
    image_url: str | None = Field(None, description="URL hình ảnh (nếu có)")
    category: str | None = Field(None, description="Danh mục câu hỏi", example="DVA-C02")

    class Config:
        from_attributes = True
