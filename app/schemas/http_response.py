# app/schemas/http_response.py
from pydantic import BaseModel, Field
from typing import Any, Optional, Union, List, Dict


class SuccessResponse(BaseModel):
    """Schema for success HTTP response"""
    data: Union[List[Any], Dict[str, Any]] = Field(..., description="Response data")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata")


class ErrorDetail(BaseModel):
    """Schema for error detail in HTTP response"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    trace_id: str = Field(..., description="Trace ID")
    details: Optional[Union[List[Any], Dict[str, Any]]] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Schema for error HTTP response"""
    error: ErrorDetail = Field(..., description="Error information")

