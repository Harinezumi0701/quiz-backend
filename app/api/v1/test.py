# app/api/v1/test.py
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.question import (
    TestDetailListResponse,
    TestDetailResponse,
    QuestionListResponse,
    QuestionResponse,
)
from app.schemas.submission import SubmissionBulkCreate, SubmissionListResponse
from app.schemas.http_response import ErrorResponse
from app.services import category_service, question_service, submission_service
from app.db.session import get_db
from app.utils.search_pagination import get_pagination_meta
from app.api.dependencies.auth import get_current_user
from app.models.users import User

router = APIRouter()


@router.get(
    "",
    response_model=TestDetailListResponse,
    summary="Get all tests",
    description="Get all tests with optional name search and pagination. Supports both single filter (key, value) and multiple filters (filter-key-1, filter-value-1, ...). For comma-separated values, use OR condition.",
    responses={
        200: {
            "description": "List of tests",
        },
    },
)
def get_all_tests(
    request: Request,
    key: Optional[str] = Query(None, description="Search key: name (legacy format)"),
    value: Optional[str] = Query(None, description="Search value for test name (legacy format)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    filter_key_1: Optional[str] = Query(None, alias="filter-key-1", description="First filter key (e.g., name)"),
    filter_value_1: Optional[str] = Query(None, alias="filter-value-1", description="First filter value (supports comma-separated for OR)"),
    filter_key_2: Optional[str] = Query(None, alias="filter-key-2", description="Second filter key"),
    filter_value_2: Optional[str] = Query(None, alias="filter-value-2", description="Second filter value"),
    db: Session = Depends(get_db),
):
    """
    Get all tests with optional filtering and pagination.

    **Filter Options:**
    - **Legacy format**: Use `key` and `value` parameters for single filter
    - **Multiple filters**: Use `filter-key-1`, `filter-value-1`, `filter-key-2`, `filter-value-2`, etc.
    - **OR condition**: Use comma-separated values in filter-value (e.g., `filter-value-1=test1,test2,test3`)
    
    **Search Keys:**
    - `name`: Search in test name (text search)
    
    **Examples:**
    - Single filter: `?key=name&value=exam`
    - Multiple filters: `?filter-key-1=name&filter-value-1=exam&filter-key-2=name&filter-value-2=test`
    - OR condition: `?filter-key-1=name&filter-value-1=exam1,exam2,exam3`

    This endpoint does not require authentication.
    """
    request_params = dict(request.query_params)
    tests, total = category_service.get_all_tests(
        db, search_key=key, search_value=value, page=page, page_size=page_size, request_params=request_params
    )

    meta = get_pagination_meta(total, page, page_size)

    return TestDetailListResponse(data=tests, meta=meta)


@router.get(
    "/{test_id}",
    response_model=TestDetailResponse,
    summary="Get test by ID",
    description="Get a specific test by ID",
    responses={
        200: {
            "description": "Test details",
        },
        404: {
            "description": "Test not found",
            "model": ErrorResponse,
        },
    },
)
def get_test_by_id(
    test_id: str = Path(
        ...,
        description="Test ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    db: Session = Depends(get_db),
):
    """
    Get a specific test by ID.

    - **test_id**: UUID of the test

    This endpoint does not require authentication.
    """
    test = category_service.get_test_by_id_only(db, test_id)

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test with ID {test_id} not found",
        )

    return TestDetailResponse(data=test, meta={})


@router.get(
    "/{test_id}/questions",
    response_model=QuestionListResponse,
    summary="Get questions by test ID",
    description="Get all questions of a specific test with optional filtering and pagination. Supports both single filter (key, value) and multiple filters (filter-key-1, filter-value-1, ...). For comma-separated values, use OR condition.",
    responses={
        200: {
            "description": "List of questions with answers",
        },
        404: {
            "description": "Test not found",
            "model": ErrorResponse,
        },
    },
)
def get_questions_by_test(
    request: Request,
    test_id: str = Path(
        ...,
        description="Test ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    key: Optional[str] = Query(None, description="Search key: content, created_at (legacy format)"),
    value: Optional[str] = Query(None, description="Search value (legacy format)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    filter_key_1: Optional[str] = Query(None, alias="filter-key-1", description="First filter key (e.g., content, created_at)"),
    filter_value_1: Optional[str] = Query(None, alias="filter-value-1", description="First filter value (supports comma-separated for OR)"),
    filter_key_2: Optional[str] = Query(None, alias="filter-key-2", description="Second filter key"),
    filter_value_2: Optional[str] = Query(None, alias="filter-value-2", description="Second filter value"),
    db: Session = Depends(get_db),
):
    """
    Get all questions of a specific test with optional filtering and pagination.

    **Filter Options:**
    - **Legacy format**: Use `key` and `value` parameters for single filter
    - **Multiple filters**: Use `filter-key-1`, `filter-value-1`, `filter-key-2`, `filter-value-2`, etc.
    - **OR condition**: Use comma-separated values in filter-value (e.g., `filter-value-1=id1,id2,id3`)
    
    **Search Keys:**
    - `content`: Search in question content (text search)
    - `created_at`: Search by creation date (date search)
    
    **Examples:**
    - Single filter: `?key=content&value=test`
    - Multiple filters: `?filter-key-1=content&filter-value-1=test&filter-key-2=created_at&filter-value-2=2024-01-01`

    This endpoint does not require authentication.
    """
    request_params = dict(request.query_params)
    questions, total = question_service.get_questions_by_test_id(
        db,
        test_id,
        search_key=key,
        search_value=value,
        page=page,
        page_size=page_size,
        request_params=request_params,
    )

    # If no results and first page, verify test exists
    if total == 0 and page == 1:
        test = category_service.get_test_by_id_only(db, test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test with ID {test_id} not found",
            )

    meta = get_pagination_meta(total, page, page_size)

    return QuestionListResponse(data=questions, meta=meta)


@router.get(
    "/{test_id}/questions/{question_id}",
    response_model=QuestionResponse,
    summary="Get question by test ID and question ID",
    description="Get a specific question of a specific test",
    responses={
        200: {
            "description": "Question with answers",
        },
        404: {
            "description": "Test or question not found",
            "model": ErrorResponse,
        },
    },
)
def get_question_by_test(
    test_id: str = Path(
        ...,
        description="Test ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    question_id: str = Path(
        ...,
        description="Question ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    db: Session = Depends(get_db),
):
    """
    Get a specific question of a specific test.

    - **test_id**: UUID of the test
    - **question_id**: UUID of the question

    This endpoint does not require authentication.
    """
    question = question_service.get_question_by_test_and_id(
        db, test_id, question_id
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found in test {test_id}",
        )

    return QuestionResponse(data=question, meta={})


@router.post(
    "/{test_id}/submit",
    response_model=SubmissionListResponse,
    summary="Submit multiple submissions for a test",
    description="Submit multiple submissions for a test in one request (requires authentication)",
    responses={
        200: {
            "description": "List of saved submissions",
        },
        401: {
            "description": "Unauthorized access",
            "model": ErrorResponse,
        },
        404: {
            "description": "Test not found or question not found or answer not found",
            "model": ErrorResponse,
        },
    }
)
def submit_test_submissions(
    test_id: str = Path(
        ...,
        description="Test ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    bulk_data: SubmissionBulkCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit multiple submissions for a test at once.
    
    - **test_id**: Test ID
    - **submissions**: List of submissions (minimum 1 submission)
    
    Each submission in the list includes:
    - question_id: Question ID
    - answer_id: Selected answer option ID
    - is_correct: Whether the submission is correct
    
    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    # Verify test exists
    test = category_service.get_test_by_id_only(db, test_id)
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test with ID {test_id} not found",
        )
    
    submissions = submission_service.submit_submissions_bulk(db, current_user.id, bulk_data.submissions)
    return SubmissionListResponse(data=submissions, meta={})
