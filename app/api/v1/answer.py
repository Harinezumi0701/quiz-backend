# app/api/v1/answer.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.question import AnswerListResponse, AnswerResponse
from app.schemas.http_response import ErrorResponse
from app.services import question_service
from app.db.session import get_db
from app.utils.search_pagination import get_pagination_meta

router = APIRouter()


@router.get(
    "",
    response_model=AnswerListResponse,
    summary="Get all answers",
    description="Get all answers with optional filtering and pagination",
    responses={
        200: {
            "description": "List of answers",
        },
    },
)
def get_all_answers(
    key: Optional[str] = Query(
        None, description="Search key: content, is_correct, or question_id"
    ),
    value: Optional[str] = Query(None, description="Search value"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
):
    """
    Get all answers with optional filtering and pagination.

    - **key**: Search key (content, is_correct, or question_id)
    - **value**: Value to search for
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10, max: 100)

    This endpoint does not require authentication.
    """
    answers, total = question_service.get_all_answers(
        db, search_key=key, search_value=value, page=page, page_size=page_size
    )

    meta = get_pagination_meta(total, page, page_size)

    return AnswerListResponse(data=answers, meta=meta)


@router.get(
    "/{answer_id}",
    response_model=AnswerResponse,
    summary="Get answer by ID",
    description="Get a specific answer by ID",
    responses={
        200: {
            "description": "Answer details",
        },
        404: {
            "description": "Answer not found",
            "model": ErrorResponse,
        },
    },
)
def get_answer_by_id(
    answer_id: str = Path(
        ...,
        description="Answer ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    db: Session = Depends(get_db),
):
    """
    Get a specific answer by ID.

    - **answer_id**: UUID of the answer

    This endpoint does not require authentication.
    """
    answer = question_service.get_answer_by_id_only(db, answer_id)

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {answer_id} not found",
        )

    return AnswerResponse(data=answer, meta={})
