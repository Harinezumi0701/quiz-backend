# app/api/v1/answer.py
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.answer import (
    AnswerListResponse,
    AnswerResponse,
    AnswerCreateRequest,
    AnswerUpdateRequest,
)
from app.schemas.http_response import ErrorResponse
from app.services import answer_service
from app.db.session import get_db
from app.utils.search_pagination import get_pagination_meta
from app.api.dependencies.permissions import require_namespace_permission
from app.models.users import User
from app.constants.permissions import PERMISSION_NAMESPACE_ANSWERS

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
    answers, total = answer_service.get_all_answers(
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
    answer = answer_service.get_answer_by_id_only(db, answer_id)

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {answer_id} not found",
        )

    return AnswerResponse(data=answer, meta={})


@router.post(
    "",
    response_model=AnswerResponse,
    summary="Create a new answer",
    description="Create a new answer (requires permission)",
    responses={
        200: {
            "description": "Answer created",
        },
        400: {
            "description": "Question not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def create_answer(
    answer_data: AnswerCreateRequest = Body(...),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ANSWERS, "POST")
    ),
):
    """
    Create a new answer.

    - **question_id**: Question ID (required)
    - **content**: Optional answer content
    - **image_url**: Optional image URL
    - **is_correct**: Whether this is the correct answer (default: false)
    - **explanation**: Optional explanation for the answer

    Requires permission: answers::create
    """
    answer = answer_service.create_answer(
        db,
        str(answer_data.question_id),
        answer_data.content,
        answer_data.image_url,
        answer_data.is_correct,
        answer_data.explanation,
    )
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question not found",
        )

    return AnswerResponse(data=answer, meta={})


@router.put(
    "/{answer_id}",
    response_model=AnswerResponse,
    summary="Update an answer",
    description="Update an answer by ID (requires permission)",
    responses={
        200: {
            "description": "Answer updated",
        },
        404: {
            "description": "Answer not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def update_answer(
    answer_id: str = Path(
        ...,
        description="Answer ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    answer_data: AnswerUpdateRequest = Body(...),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ANSWERS, "PUT")
    ),
):
    """
    Update an answer by ID.

    - **answer_id**: UUID of the answer
    - **content**: Optional new answer content
    - **image_url**: Optional new image URL
    - **is_correct**: Optional new is_correct value
    - **explanation**: Optional new explanation

    Requires permission: answers::update
    """
    answer = answer_service.update_answer(
        db,
        answer_id,
        answer_data.content,
        answer_data.image_url,
        answer_data.is_correct,
        answer_data.explanation,
    )
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {answer_id} not found",
        )

    return AnswerResponse(data=answer, meta={})


@router.delete(
    "/{answer_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an answer",
    description="Delete an answer by ID (soft delete, requires permission)",
    responses={
        200: {
            "description": "Answer deleted successfully",
        },
        404: {
            "description": "Answer not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def delete_answer(
    answer_id: str = Path(
        ...,
        description="Answer ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ANSWERS, "DELETE")
    ),
):
    """
    Delete an answer by ID (soft delete).

    - **answer_id**: UUID of the answer

    Requires permission: answers::delete
    """
    deleted = answer_service.delete_answer(db, answer_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {answer_id} not found",
        )

    return {"message": "Answer deleted successfully"}
