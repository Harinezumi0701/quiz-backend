# app/utils/error_utils.py
"""
Error utility functions for mapping error messages to error codes.
"""
from app.constants.error_codes import (
    EMAIL_ALREADY_REGISTERED,
    INCORRECT_EMAIL_OR_PASSWORD,
    UNAUTHORIZED,
    USER_NOT_FOUND,
    QUESTIONS_NOT_FOUND,
    HTTP_400,
    HTTP_401,
    HTTP_403,
    HTTP_404,
    HTTP_409,
    HTTP_422,
    HTTP_500,
    HTTP_503,
)


# Mapping from error messages to error codes
ERROR_MESSAGE_TO_CODE = {
    # Authentication errors
    "Email already registered": EMAIL_ALREADY_REGISTERED,
    "Incorrect email or password": INCORRECT_EMAIL_OR_PASSWORD,
    "Could not validate credentials": UNAUTHORIZED,
    
    # User errors
    "User not found": USER_NOT_FOUND,
    
    # Question errors
    "No questions found for category": QUESTIONS_NOT_FOUND,
    "No questions found for category:": QUESTIONS_NOT_FOUND,
    "No questions found for category: {category}": QUESTIONS_NOT_FOUND,
    "No questions found for category: {category}, test: {test}": QUESTIONS_NOT_FOUND,
    
    # HTTP status code fallbacks
    "400": HTTP_400,
    "401": HTTP_401,
    "403": HTTP_403,
    "404": HTTP_404,
    "409": HTTP_409,
    "422": HTTP_422,
    "500": HTTP_500,
    "503": HTTP_503,
}


def get_error_code_from_message(message: str, status_code: int = None) -> str:
    """
    Get error code from error message.
    
    Args:
        message: Error message string
        status_code: HTTP status code (optional, used as fallback)
    
    Returns:
        Error code string
    """
    # Check exact match first
    if message in ERROR_MESSAGE_TO_CODE:
        return ERROR_MESSAGE_TO_CODE[message]
    
    # Check partial matches (for formatted messages)
    for error_msg, error_code in ERROR_MESSAGE_TO_CODE.items():
        if error_msg in message:
            return error_code
    
    # Fallback to HTTP status code based error code
    if status_code:
        status_code_map = {
            400: HTTP_400,
            401: HTTP_401,
            403: HTTP_403,
            404: HTTP_404,
            409: HTTP_409,
            422: HTTP_422,
            500: HTTP_500,
            503: HTTP_503,
        }
        return status_code_map.get(status_code, f"HTTP_{status_code}")
    
    return HTTP_500


def get_error_code_from_status_code(status_code: int) -> str:
    """
    Get error code from HTTP status code.
    
    Args:
        status_code: HTTP status code
    
    Returns:
        Error code string
    """
    status_code_map = {
        400: HTTP_400,
        401: HTTP_401,
        403: HTTP_403,
        404: HTTP_404,
        409: HTTP_409,
        422: HTTP_422,
        500: HTTP_500,
        503: HTTP_503,
    }
    return status_code_map.get(status_code, f"HTTP_{status_code}")

