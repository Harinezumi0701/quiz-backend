# app/api/v1/question_set.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.question import (
    QuestionSetDetailListResponse,
    QuestionSetDetailResponse,
)
from app.schemas.http_response import ErrorResponse
from app.services import category_service
from app.db.session import get_db
from app.utils.search_pagination import get_pagination_meta

router = APIRouter()


@router.get(
    "/",
    response_model=QuestionSetDetailListResponse,
    summary="Get all question sets",
    description="Get all question sets with optional name search and pagination",
    responses={
        200: {
            "description": "List of question sets",
        },
    },
)
def get_all_question_sets(
    key: Optional[str] = Query(None, description="Search key: name"),
    value: Optional[str] = Query(None, description="Search value for question set name"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
):
    """
    Get all question sets with optional filtering and pagination.

    - **key**: Search key (only "name" is supported)
    - **value**: Value to search for in question set name
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10, max: 100)

    This endpoint does not require authentication.
    """
    question_sets, total = category_service.get_all_question_sets(
        db, search_key=key, search_value=value, page=page, page_size=page_size
    )

    meta = get_pagination_meta(total, page, page_size)

    return QuestionSetDetailListResponse(data=question_sets, meta=meta)


@router.get(
    "/{question_set_id}",
    response_model=QuestionSetDetailResponse,
    summary="Get question set by ID",
    description="Get a specific question set by ID",
    responses={
        200: {
            "description": "Question set details",
        },
        404: {
            "description": "Question set not found",
            "model": ErrorResponse,
        },
    },
)
def get_question_set_by_id(
    question_set_id: str = Path(
        ...,
        description="Question set ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    db: Session = Depends(get_db),
):
    """
    Get a specific question set by ID.

    - **question_set_id**: UUID of the question set

    This endpoint does not require authentication.
    """
    question_set = category_service.get_question_set_by_id_only(db, question_set_id)

    if not question_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question set with ID {question_set_id} not found",
        )

    return QuestionSetDetailResponse(data=question_set, meta={})
