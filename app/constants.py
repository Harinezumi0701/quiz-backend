# app/constants.py
"""
Constants used throughout the application.
"""

# API Paths
API_V1_PREFIX = "/api/v1"
AUTH_PREFIX = f"{API_V1_PREFIX}/auth"
USERS_PREFIX = f"{API_V1_PREFIX}/users"
QUESTIONS_PREFIX = f"{API_V1_PREFIX}/questions"
SUBMISSIONS_PREFIX = f"{API_V1_PREFIX}/submissions"
HEALTH_CHECK_PATH = f"{API_V1_PREFIX}/health"
ROOT_PATH = "/"

# App Configuration
APP_TITLE = "My FastAPI Project"
APP_VERSION = "1.0.0"
SERVICE_NAME = "quiz-api"
HEALTH_STATUS = "healthy"
WELCOME_MESSAGE = "Welcome to My FastAPI Project"

# CORS Configuration
CORS_ALLOW_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174"
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Security Constants
PASSWORD_SCHEME = "bcrypt"
JWT_ALGORITHM = "HS256"
JWT_TOKEN_TYPE = "Bearer"
JWT_SUBJECT_KEY = "sub"
DEFAULT_SECRET_KEY = "your-secret-key-change-this-in-production"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Error Messages
ERROR_EMAIL_ALREADY_REGISTERED = "Email already registered"
ERROR_INCORRECT_EMAIL_OR_PASSWORD = "Incorrect email or password"
ERROR_COULD_NOT_VALIDATE_CREDENTIALS = "Could not validate credentials"
ERROR_USER_NOT_FOUND = "User not found"
ERROR_QUESTIONS_NOT_FOUND_CATEGORY = "No questions found for category: {category}"
ERROR_QUESTIONS_NOT_FOUND_CATEGORY_SET = "No questions found for category: {category}, set: {question_set}"

# HTTP Status Codes
HTTP_STATUS_CREATED = 201
HTTP_STATUS_NOT_FOUND = 404

