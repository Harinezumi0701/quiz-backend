from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from app.schemas.http_response import SuccessResponse


class UserCategorySettingsOut(BaseModel):
    id: UUID
    user_id: UUID
    category_id: UUID
    category_name: str
    questions_per_day: int
    time_limit: int
    created_at: int | None
    updated_at: int | None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "category_id": "550e8400-e29b-41d4-a716-446655440002",
                "category_name": "SAA",
                "questions_per_day": 20,
                "time_limit": 30,
                "created_at": 1704067200,
                "updated_at": 1704067200,
            }
        }


class UserCategorySettingsResponse(SuccessResponse[UserCategorySettingsOut]):
    pass


class UserCategorySettingsListResponse(SuccessResponse[List[UserCategorySettingsOut]]):
    pass


class UserCategorySettingsUpsertRequest(BaseModel):
    questions_per_day: int = Field(default=20, ge=1, description="Questions to practice per day", example=20)
    time_limit: int = Field(default=60, ge=1, description="Session time limit in minutes", example=30)

    class Config:
        json_schema_extra = {
            "example": {"questions_per_day": 20, "time_limit": 30}
        }
