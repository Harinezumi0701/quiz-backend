# app/constants/security.py
"""
Security-related constants.
"""

PASSWORD_SCHEME = "bcrypt"
JWT_ALGORITHM = "HS256"
JWT_TOKEN_TYPE = "Bearer"
JWT_SUBJECT_KEY = "sub"
DEFAULT_SECRET_KEY = "your-secret-key-change-this-in-production"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = 7

