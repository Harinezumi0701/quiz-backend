# app/api/v1/answer.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
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
    description="Get all answers with optional filtering and pagination. Supports both single filter (key, value) and multiple filters (filter-key-1, filter-value-1, ...). For comma-separated values, use OR condition.",
    responses={
        200: {
            "description": "List of answers",
        },
    },
)
def get_all_answers(
    request: Request,
    key: Optional[str] = Query(
        None,
        description="Search key: content, is_correct, or question_id (legacy format)",
    ),
    value: Optional[str] = Query(None, description="Search value (legacy format)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    filter_key_1: Optional[str] = Query(
        None,
        alias="filter-key-1",
        description="First filter key (e.g., content, is_correct, question_id)",
    ),
    filter_value_1: Optional[str] = Query(
        None,
        alias="filter-value-1",
        description="First filter value (supports comma-separated for OR)",
    ),
    filter_key_2: Optional[str] = Query(
        None, alias="filter-key-2", description="Second filter key"
    ),
    filter_value_2: Optional[str] = Query(
        None, alias="filter-value-2", description="Second filter value"
    ),
    filter_key_3: Optional[str] = Query(
        None, alias="filter-key-3", description="Third filter key"
    ),
    filter_value_3: Optional[str] = Query(
        None, alias="filter-value-3", description="Third filter value"
    ),
    db: Session = Depends(get_db),
):
    """
    Get all answers with optional filtering and pagination.

    **Filter Options:**
    - **Legacy format**: Use `key` and `value` parameters for single filter
    - **Multiple filters**: Use `filter-key-1`, `filter-value-1`, `filter-key-2`, `filter-value-2`, etc.
    - **OR condition**: Use comma-separated values in filter-value (e.g., `filter-value-3=id1,id2,id3`)

    **Search Keys:**
    - `content`: Search in answer content (text search)
    - `is_correct`: Filter by correctness (exact match: true/false)
    - `question_id`: Filter by question ID (exact match, supports comma-separated for OR)

    **Examples:**
    - Single filter: `?key=content&value=answer`
    - Multiple filters: `?filter-key-1=content&filter-value-1=test&filter-key-2=is_correct&filter-value-2=true`
    - OR condition: `?filter-key-1=question_id&filter-value-1=id1,id2,id3`

    This endpoint does not require authentication.
    """
    request_params = dict(request.query_params)
    answers, total = question_service.get_all_answers(
        db,
        search_key=key,
        search_value=value,
        page=page,
        page_size=page_size,
        request_params=request_params,
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
