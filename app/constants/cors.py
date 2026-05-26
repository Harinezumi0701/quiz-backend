# app/constants/cors.py
"""
CORS configuration constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "")
CORS_ALLOW_ORIGINS: list[str] = (
    [o.strip() for o in _origins_env.split(",") if o.strip()]
    if _origins_env
    else [
        "http://localhost:5173",
        "http://localhost:5174",
    ]
)

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

