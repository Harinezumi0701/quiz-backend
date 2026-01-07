# app/utils/response.py
from typing import Any, Optional, Union
from fastapi import status
from fastapi.responses import JSONResponse
from app.schemas.http_response import SuccessResponse, ErrorResponse, ErrorDetail
import uuid


def success_response(
    data: Union[list, dict],
    meta: Optional[dict] = None,
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    Tạo success response theo chuẩn.

    Args:
        data: Dữ liệu response (object hoặc array)
        meta: Metadata (pagination, etc.)
        status_code: HTTP status code (mặc định 200)

    Returns:
        JSONResponse với cấu trúc chuẩn
    """
    if meta is None:
        meta = {}

    response_data = SuccessResponse(data=data, meta=meta)
    return JSONResponse(
        content=response_data.model_dump(),
        status_code=status_code
    )


def error_response(
    code: str,
    message: str,
    trace_id: Optional[str] = None,
    details: Optional[Union[list, dict]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """
    Tạo error response theo chuẩn.

    Args:
        code: Error code
        message: Error message
        trace_id: Trace ID (nếu None sẽ tự động generate)
        details: Additional error details
        status_code: HTTP status code (mặc định 400)

    Returns:
        JSONResponse với cấu trúc chuẩn
    """
    if trace_id is None:
        trace_id = str(uuid.uuid4())

    error_detail = ErrorDetail(
        code=code,
        message=message,
        trace_id=trace_id,
        details=details
    )
    response_data = ErrorResponse(error=error_detail)
    return JSONResponse(
        content=response_data.model_dump(),
        status_code=status_code
    )

