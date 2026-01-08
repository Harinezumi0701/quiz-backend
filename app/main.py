# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.api.v1 import user, auth, question, submission
from app.utils.exceptions import http_exception_handler, general_exception_handler
from app.utils.response import success_response
from app.constants import (
    APP_TITLE,
    APP_VERSION,
    SERVICE_NAME,
    HEALTH_STATUS,
    WELCOME_MESSAGE,
    CORS_ALLOW_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    AUTH_PREFIX,
    USERS_PREFIX,
    QUESTIONS_PREFIX,
    SUBMISSIONS_PREFIX,
    HEALTH_CHECK_PATH,
    ROOT_PATH,
)

description = """
## Quiz Backend API

Quiz system backend API with the following features:

* **Authentication**: User registration and login
* **Questions**: Question and category management
* **Submissions**: Process and store user submissions
* **Users**: User information management
* **Dashboard**: Statistics and result reports

### Authentication

Most endpoints require authentication. After successful login, you will receive an access token.
Use this token in the header: `Authorization: Bearer <token>`
"""

tags_metadata = [
    {
        "name": "auth",
        "description": "User authentication. Register and login to receive access token.",
    },
    {
        "name": "users",
        "description": "User information management. Get list of users or current user information.",
    },
    {
        "name": "questions",
        "description": "Question management. Get list of categories, question sets and questions by category/set.",
    },
    {
        "name": "submissions",
        "description": "Process user submissions. Submit submissions and view dashboard statistics.",
    },
]

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=description,
    tags_metadata=tags_metadata,
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_url="/docs/openapi.json",  # Ensure OpenAPI endpoint is enabled
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Response wrapper middleware to automatically wrap success responses
from app.middleware.response_wrapper import ResponseWrapperMiddleware
app.add_middleware(ResponseWrapperMiddleware)

# Register exception handlers
from fastapi import HTTPException
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register routers from api/v1 folder
app.include_router(auth.router, prefix=AUTH_PREFIX, tags=["auth"])
app.include_router(user.router, prefix=USERS_PREFIX, tags=["users"])
app.include_router(question.router, prefix=QUESTIONS_PREFIX, tags=["questions"])
app.include_router(submission.router, prefix=SUBMISSIONS_PREFIX, tags=["submissions"])


def custom_openapi():
    """Custom OpenAPI schema ensuring openapi version field is present."""
    if app.openapi_schema:
        return app.openapi_schema
    try:
        openapi_schema = get_openapi(
            title=APP_TITLE,
            version=APP_VERSION,
            openapi_version="3.1.0",
            description=description,
            routes=app.routes,
            tags=tags_metadata,
            contact={
                "name": "API Support",
                "email": "support@example.com",
            },
            license_info={
                "name": "MIT",
            },
        )
        # Ensure openapi field is always present
        if "openapi" not in openapi_schema:
            openapi_schema["openapi"] = "3.1.0"
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    except Exception as e:
        # Fallback: create basic schema if error occurs
        import logging
        logging.error(f"Error generating OpenAPI schema: {e}")
        fallback_schema = {
            "openapi": "3.1.0",
            "info": {
                "title": APP_TITLE,
                "version": APP_VERSION,
                "description": description,
            },
            "paths": {},
        }
        app.openapi_schema = fallback_schema
        return fallback_schema


# Assign custom_openapi after all routes are registered
app.openapi = custom_openapi

@app.get(
    ROOT_PATH,
    summary="Root endpoint",
    description="Returns the API welcome message",
    tags=["general"],
    responses={
        200: {
            "description": "Welcome message",
            "content": {
                "application/json": {
                    "example": {
                        "data": {"message": WELCOME_MESSAGE},
                        "meta": {}
                    }
                }
            }
        }
    }
)
def root():
    """
    Root endpoint of the API.
    
    Returns:
        dict: Welcome message
    """
    return success_response(
        data={"message": WELCOME_MESSAGE},
        meta={}
    )


@app.get(
    HEALTH_CHECK_PATH,
    summary="Health check",
    description="Check the service operational status",
    tags=["general"],
    responses={
        200: {
            "description": "Service status",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "status": HEALTH_STATUS,
                            "service": SERVICE_NAME,
                            "version": APP_VERSION
                        },
                        "meta": {}
                    }
                }
            }
        }
    }
)
def health_check():
    """
    Health check endpoint to verify if the service is running.
    
    Returns:
        dict: Service status, service name and version
    """
    return success_response(
        data={
            "status": HEALTH_STATUS,
            "service": SERVICE_NAME,
            "version": APP_VERSION
        },
        meta={}
    )
