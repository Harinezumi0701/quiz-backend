# app/schemas/user_test_assignment.py
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from app.schemas.http_response import SuccessResponse


class UserTestAssignmentOut(BaseModel):
    """Schema for user test assignment"""
    id: UUID = Field(..., description="Assignment ID")
    user_id: UUID = Field(..., description="User ID")
    test_id: UUID = Field(..., description="Test ID")
    assigned_at: int | None = Field(None, description="Assigned at Unix timestamp")
    expires_at: int | None = Field(None, description="Expires at Unix timestamp (null = never expires)")

    class Config:
        from_attributes = True


class UserTestAssignmentWithDetails(BaseModel):
    """Schema for user test assignment with test details (for user's view)"""
    id: UUID = Field(..., description="Assignment ID")
    test_id: UUID = Field(..., description="Test ID")
    test_name: str = Field(..., description="Test name")
    test_description: str | None = Field(None, description="Test description")
    test_time_limit: int = Field(..., description="Test time limit in minutes")
    question_count: int = Field(..., description="Number of questions in the test")
    category_id: UUID = Field(..., description="Category ID")
    assigned_at: int | None = Field(None, description="Assigned at Unix timestamp")
    expires_at: int | None = Field(None, description="Expires at Unix timestamp (null = never expires)")

    class Config:
        from_attributes = True


class UserTestAssignmentAdmin(BaseModel):
    """Schema for user test assignment with user details (for admin view)"""
    id: UUID = Field(..., description="Assignment ID")
    user_id: UUID = Field(..., description="User ID")
    user_email: str = Field(..., description="User email")
    user_full_name: str = Field(..., description="User full name")
    test_id: UUID = Field(..., description="Test ID")
    test_name: str = Field(..., description="Test name")
    assigned_at: int | None = Field(None, description="Assigned at Unix timestamp")
    expires_at: int | None = Field(None, description="Expires at Unix timestamp")

    class Config:
        from_attributes = True


class UserTestAssignmentListResponse(SuccessResponse[List[UserTestAssignmentWithDetails]]):
    """Response schema for list of user test assignments"""
    pass


class UserTestAssignmentAdminListResponse(SuccessResponse[List[UserTestAssignmentAdmin]]):
    """Response schema for admin list of test assignments"""
    pass


class UserTestAssignmentResponse(SuccessResponse[UserTestAssignmentOut]):
    """Response schema for single test assignment"""
    pass


class UserTestAssignmentCreateRequest(BaseModel):
    """Request schema for creating a test assignment"""
    user_id: UUID = Field(..., description="User ID to assign the test to")
    test_id: UUID = Field(..., description="Test ID to assign")
    expires_at: int | None = Field(None, description="Expiration Unix timestamp (null = never expires)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "test_id": "550e8400-e29b-41d4-a716-446655440001",
                "expires_at": None,
            }
        }


class BulkAssignmentCreateRequest(BaseModel):
    """Request schema for creating bulk test assignments"""
    user_ids: List[UUID] = Field(..., min_length=1, description="List of User IDs to assign the test to")
    test_id: UUID = Field(..., description="Test ID to assign")
    expires_at: int | None = Field(None, description="Expiration Unix timestamp (null = never expires)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "550e8400-e29b-41d4-a716-446655440002",
                ],
                "test_id": "550e8400-e29b-41d4-a716-446655440001",
                "expires_at": None,
            }
        }


class BulkAssignmentResponse(BaseModel):
    """Response schema for bulk assignment creation"""
    created: int = Field(..., description="Number of assignments created")
    skipped: int = Field(..., description="Number of assignments skipped (already exists or user not found)")
    total: int = Field(..., description="Total number of user IDs provided")


class BulkAssignmentCreateResponse(SuccessResponse[BulkAssignmentResponse]):
    """Response schema for bulk assignment creation wrapped"""
    pass
