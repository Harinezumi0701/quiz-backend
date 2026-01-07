# app/middleware/response_wrapper.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, StreamingResponse
from fastapi.responses import JSONResponse as FastAPIJSONResponse
from app.utils.response import success_response
from typing import Callable
import json


class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    """
    Middleware để tự động wrap success responses theo chuẩn.
    Chỉ wrap responses không phải là error responses (không có status code 4xx, 5xx).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Chỉ wrap success responses (status code 2xx)
        if 200 <= response.status_code < 300:
            # Bỏ qua nếu response đã là JSONResponse
            if isinstance(response, (JSONResponse, FastAPIJSONResponse)):
                try:
                    # Lấy content từ response
                    # Với FastAPI JSONResponse, body có thể là bytes hoặc đã được serialize
                    body = response.body
                    
                    # Parse JSON để kiểm tra xem đã có cấu trúc chuẩn chưa
                    try:
                        if isinstance(body, bytes):
                            parsed_content = json.loads(body.decode())
                        else:
                            parsed_content = body
                        
                        # Nếu đã có 'data' và 'meta' hoặc 'error', không wrap lại
                        if isinstance(parsed_content, dict) and ("data" in parsed_content or "error" in parsed_content):
                            return response
                    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError):
                        pass
                    
                    # Nếu chưa có cấu trúc chuẩn, wrap lại
                    try:
                        if isinstance(body, bytes):
                            parsed_content = json.loads(body.decode())
                        else:
                            parsed_content = body
                        
                        # Wrap vào cấu trúc chuẩn
                        wrapped_response = success_response(
                            data=parsed_content,
                            meta={},
                            status_code=response.status_code
                        )
                        # Copy headers từ response gốc
                        for key, value in response.headers.items():
                            if key.lower() not in ['content-length', 'content-type']:
                                wrapped_response.headers[key] = value
                        return wrapped_response
                    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError):
                        # Nếu không parse được JSON, trả về response gốc
                        return response
                except Exception:
                    # Nếu có lỗi, trả về response gốc
                    return response

        # Với error responses (4xx, 5xx), exception handlers đã xử lý
        return response

