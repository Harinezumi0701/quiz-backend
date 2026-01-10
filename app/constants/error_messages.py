# app/constants/error_messages.py
"""
Error message constants.
These are user-facing error messages used throughout the application.
"""

ERROR_EMAIL_ALREADY_REGISTERED = "Email already registered"
ERROR_INCORRECT_EMAIL_OR_PASSWORD = "Incorrect email or password"
ERROR_COULD_NOT_VALIDATE_CREDENTIALS = "Could not validate credentials"
ERROR_USER_NOT_FOUND = "User not found"
ERROR_REFRESH_TOKEN_EXPIRED = "Refresh token expired"
ERROR_REFRESH_TOKEN_NOT_FOUND = "Refresh token not found"
ERROR_QUESTIONS_NOT_FOUND_CATEGORY = "No questions found for category: {category}"
ERROR_QUESTIONS_NOT_FOUND_CATEGORY_TEST = (
    "No questions found for category: {category}, test: {test}"
)
ERROR_USER_ID_ALREADY_EXISTS = "User ID already exists"
ERROR_INVALID_USER_ID_FORMAT = "User ID must match pattern [A-Za-z\\._-] and be between 1-125 characters"
ERROR_INVALID_REFRESH_TOKEN = "Invalid refresh token"
ERROR_INCORRECT_OLD_PASSWORD = "Incorrect old password"
ERROR_NEW_PASSWORD_SAME_AS_OLD = "New password must be different from old password"
