# app/api/v1/submission.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.submission import (
    SubmissionOut,
    SubmissionResponse
)
from app.schemas.http_response import ErrorResponse
from app.services import submission_service
from app.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.models.users import User

router = APIRouter()

