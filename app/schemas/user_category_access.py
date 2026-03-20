# app/schemas/user_category_access.py
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Any


class CategoryAccessGrantRequest(BaseModel):
    category_id: UUID


class CategoryAccessResponse(BaseModel):
    id: UUID
    user_id: UUID
    category_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryAccessListResponse(BaseModel):
    data: list[CategoryAccessResponse]
    meta: Any = {}
