# app/constants/cors.py
"""
CORS configuration constants.
"""
import os

_default_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
]

_env_origins = os.getenv("CORS_ALLOW_ORIGINS", "")
CORS_ALLOW_ORIGINS = (
    [origin.strip() for origin in _env_origins.split(",") if origin.strip()]
    if _env_origins
    else _default_origins
)

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

