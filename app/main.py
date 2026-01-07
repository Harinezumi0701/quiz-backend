# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import user, auth, question, response
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
    RESPONSES_PREFIX,
    HEALTH_CHECK_PATH,
    ROOT_PATH,
)

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Đăng ký router từ folder api/v1
app.include_router(auth.router, prefix=AUTH_PREFIX, tags=["auth"])
app.include_router(user.router, prefix=USERS_PREFIX, tags=["users"])
app.include_router(question.router, prefix=QUESTIONS_PREFIX, tags=["questions"])
app.include_router(response.router, prefix=RESPONSES_PREFIX, tags=["responses"])

@app.get(ROOT_PATH)
def root():
    return {"message": WELCOME_MESSAGE}

@app.get(HEALTH_CHECK_PATH)
def health_check():
    return {
        "status": HEALTH_STATUS,
        "service": SERVICE_NAME,
        "version": APP_VERSION
    }
