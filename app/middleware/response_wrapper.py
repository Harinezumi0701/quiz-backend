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
    Middleware to automatically wrap success responses according to standard format.
    Only wraps responses that are not error responses (no 4xx, 5xx status codes).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Only wrap success responses (status code 2xx)
        if 200 <= response.status_code < 300:
            # Skip if response is already a JSONResponse
            if isinstance(response, (JSONResponse, FastAPIJSONResponse)):
                try:
                    # Get content from response
                    # With FastAPI JSONResponse, body can be bytes or already serialized
                    body = response.body
                    
                    # Parse JSON to check if it already has standard structure
                    try:
                        if isinstance(body, bytes):
                            parsed_content = json.loads(body.decode())
                        else:
                            parsed_content = body
                        
                        # If already has 'data' and 'meta' or 'error', don't wrap again
                        if isinstance(parsed_content, dict) and ("data" in parsed_content or "error" in parsed_content):
                            return response
                    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError):
                        pass
                    
                    # If doesn't have standard structure yet, wrap it
                    try:
                        if isinstance(body, bytes):
                            parsed_content = json.loads(body.decode())
                        else:
                            parsed_content = body
                        
                        # Wrap into standard structure
                        wrapped_response = success_response(
                            data=parsed_content,
                            meta={},
                            status_code=response.status_code
                        )
                        # Copy headers from original response
                        for key, value in response.headers.items():
                            if key.lower() not in ['content-length', 'content-type']:
                                wrapped_response.headers[key] = value
                        return wrapped_response
                    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError, TypeError):
                        # If cannot parse JSON, return original response
                        return response
                except Exception:
                    # If there's an error, return original response
                    return response

        # For error responses (4xx, 5xx), exception handlers have already processed them
        return response

