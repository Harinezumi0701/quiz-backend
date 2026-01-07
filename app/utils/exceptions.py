# app/utils/exceptions.py
from typing import Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.utils.response import error_response
from app.utils.error_utils import (
    get_error_code_from_message,
    get_error_code_from_status_code,
)
from app.constants.error_codes import INTERNAL_SERVER_ERROR
import uuid
import logging

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler cho HTTPException để format response theo chuẩn.

    Args:
        request: FastAPI request object
        exc: HTTPException instance

    Returns:
        JSONResponse với cấu trúc error chuẩn
    """
    trace_id = str(uuid.uuid4())
    
    # Lấy error code từ detail hoặc từ status code
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        error_code = exc.detail["code"]
        error_message = exc.detail.get("message", str(exc.detail))
        error_details = exc.detail.get("details")
    elif isinstance(exc.detail, str):
        # Nếu detail là string, sử dụng centralized error code mapping
        error_message = exc.detail
        error_code = get_error_code_from_message(error_message, exc.status_code)
        error_details = None
    else:
        # Tự động tạo error code từ status code
        error_code = get_error_code_from_status_code(exc.status_code)
        error_message = str(exc.detail) if exc.detail else "An error occurred"
        error_details = None

    logger.error(
        f"HTTPException: {error_code} - {error_message}",
        extra={"trace_id": trace_id, "status_code": exc.status_code}
    )

    return error_response(
        code=error_code,
        message=error_message,
        trace_id=trace_id,
        details=error_details,
        status_code=exc.status_code
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler cho các exception không được xử lý.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse với cấu trúc error chuẩn
    """
    trace_id = str(uuid.uuid4())
    
    logger.exception(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={"trace_id": trace_id}
    )

    return error_response(
        code=INTERNAL_SERVER_ERROR,
        message="An internal server error occurred",
        trace_id=trace_id,
        details={"type": type(exc).__name__} if logger.level == logging.DEBUG else None,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

