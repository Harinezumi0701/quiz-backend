# app/api/v1/question.py
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    status,
)
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.question import (
    QuestionListResponse,
    QuestionResponse,
    QuestionCreateRequest,
    QuestionUpdateRequest,
)
from app.schemas.http_response import ErrorResponse
from app.services import question_service
from app.db.session import get_db
from app.utils.search_pagination import get_pagination_meta
from app.api.dependencies.permissions import require_namespace_permission
from app.models.users import User
from app.constants.permissions import PERMISSION_NAMESPACE_QUESTIONS

router = APIRouter()


@router.get(
    "",
    response_model=QuestionListResponse,
    summary="Get all questions",
    description="Get all questions with optional filtering and pagination. Supports both single filter (key, value) and multiple filters (filter-key-1, filter-value-1, ...). For comma-separated values, use OR condition (e.g., filter-value-3=id1,id2,id3).",
    responses={
        200: {
            "description": "List of questions with answers",
        }
    },
)
def get_all_questions(
    request: Request,
    key: Optional[str] = Query(
        None, description="Search key: content, created_at, or test (legacy format)"
    ),
    value: Optional[str] = Query(None, description="Search value (legacy format)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    filter_key_1: Optional[str] = Query(
        None,
        alias="filter-key-1",
        description="First filter key (e.g., content, created_at, test)",
    ),
    filter_value_1: Optional[str] = Query(
        None,
        alias="filter-value-1",
        description="First filter value (supports comma-separated for OR: id1,id2,id3)",
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
    Get all questions with optional filtering and pagination.

    **Filter Options:**
    - **Legacy format**: Use `key` and `value` parameters for single filter
    - **Multiple filters**: Use `filter-key-1`, `filter-value-1`, `filter-key-2`, `filter-value-2`, etc.
    - **OR condition**: Use comma-separated values in filter-value (e.g., `filter-value-3=id1,id2,id3`)

    **Search Keys:**
    - `content`: Search in question content (text search)
    - `created_at`: Search by creation date (date search)
    - `test`: Search by test name (text search)

    **Examples:**
    - Single filter: `?key=content&value=test`
    - Multiple filters: `?filter-key-1=content&filter-value-1=test&filter-key-2=test&filter-value-2=exam1`
    - OR condition: `?filter-key-1=id&filter-value-1=id1,id2,id3`

    This endpoint does not require authentication.
    """
    request_params = dict(request.query_params)
    questions, total = question_service.get_all_questions(
        db,
        search_key=key,
        search_value=value,
        page=page,
        page_size=page_size,
        request_params=request_params,
    )

    meta = get_pagination_meta(total, page, page_size)

    return QuestionListResponse(data=questions, meta=meta)


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Get question by ID",
    description="Get a specific question by ID with answers",
    responses={
        200: {
            "description": "Question with answers",
        },
        404: {
            "description": "Question not found",
            "model": ErrorResponse,
        },
    },
)
def get_question_by_id(
    question_id: str = Path(
        ..., description="Question ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    db: Session = Depends(get_db),
):
    """
    Get a specific question by ID with answers.

    - **question_id**: UUID of the question

    This endpoint does not require authentication.
    """
    question = question_service.get_question_by_id(db, question_id)

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found",
        )

    return QuestionResponse(data=question, meta={})


@router.post(
    "",
    response_model=QuestionResponse,
    summary="Create a new question",
    description="Create a new question (requires permission)",
    responses={
        200: {
            "description": "Question created",
        },
        400: {
            "description": "Category or test not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def create_question(
    question_data: QuestionCreateRequest = Body(...),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_QUESTIONS, "POST")
    ),
):
    """
    Create a new question.

    - **content**: Question content (required)
    - **image_url**: Optional image URL
    - **category_id**: Optional category ID
    - **test_id**: Optional test ID
    - **is_multiple_choice**: Whether this question has multiple correct answers (default: false)

    Requires permission: questions::create
    """
    question = question_service.create_question(
        db,
        question_data.content,
        question_data.image_url,
        str(question_data.category_id) if question_data.category_id else None,
        str(question_data.test_id) if question_data.test_id else None,
        question_data.is_multiple_choice,
    )
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category or test not found",
        )

    return QuestionResponse(data=question, meta={})


@router.put(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Update a question",
    description="Update a question by ID (requires permission)",
    responses={
        200: {
            "description": "Question updated",
        },
        404: {
            "description": "Question not found",
            "model": ErrorResponse,
        },
        400: {
            "description": "Category or test not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def update_question(
    question_id: str = Path(
        ...,
        description="Question ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    question_data: QuestionUpdateRequest = Body(...),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_QUESTIONS, "PUT")
    ),
):
    """
    Update a question by ID.

    - **question_id**: UUID of the question
    - **content**: Optional new question content
    - **image_url**: Optional new image URL
    - **category_id**: Optional new category ID
    - **test_id**: Optional new test ID
    - **is_multiple_choice**: Optional new is_multiple_choice value

    Requires permission: questions::update
    """
    question = question_service.update_question(
        db,
        question_id,
        question_data.content,
        question_data.image_url,
        str(question_data.category_id) if question_data.category_id else None,
        str(question_data.test_id) if question_data.test_id else None,
        question_data.is_multiple_choice,
    )
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found",
        )

    return QuestionResponse(data=question, meta={})


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a question",
    description="Delete a question by ID (soft delete, requires permission)",
    responses={
        200: {
            "description": "Question deleted successfully",
        },
        404: {
            "description": "Question not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def delete_question(
    question_id: str = Path(
        ...,
        description="Question ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_QUESTIONS, "DELETE")
    ),
):
    """
    Delete a question by ID (soft delete).

    - **question_id**: UUID of the question

    Requires permission: questions::delete
    """
    deleted = question_service.delete_question(db, question_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found",
        )

    return {"message": "Question deleted successfully"}
