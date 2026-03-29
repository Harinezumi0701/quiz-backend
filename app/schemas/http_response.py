# app/schemas/http_response.py
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """Schema for success HTTP response"""
    data: T = Field(..., description="Response data")
    meta: dict[str, Any] | None = Field(default_factory=dict, description="Metadata")


class ErrorDetail(BaseModel):
    """Schema for error detail in HTTP response"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    trace_id: str = Field(..., description="Trace ID")
    details: list[Any] | dict[str, Any] | None = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for error HTTP response"""
    error: ErrorDetail = Field(..., description="Error information")

