# app/api/v1/test.py
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
from uuid import UUID
from app.schemas.test import (
    TestDetailListResponse,
    TestDetailResponse,
    TestCreateRequest,
    TestUpdateRequest,
)
from app.schemas.submission import SubmissionBulkCreate, SubmissionListResponse, SubmissionHistoryResponse
from app.schemas.http_response import ErrorResponse
from app.services import category_service, submission_service
from app.repository import submission_repo
from app.services import permission_service
from app.repository import user_category_access_repo, user_test_assignment_repo
from app.db.session import get_db
from app.utils.search_pagination import get_pagination_meta
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_namespace_permission
from app.models.users import User
from app.constants.permissions import PERMISSION_NAMESPACE_TESTS

router = APIRouter()


@router.get(
    "",
    response_model=TestDetailListResponse,
    summary="Get all tests",
    description="Get all tests with optional name search and pagination. Supports standard query parameters for filtering (key=value). For comma-separated values, use OR condition.",
    responses={
        200: {
            "description": "List of tests",
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def get_all_tests(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_TESTS, "GET")
    ),
):
    """
    Get all tests with optional filtering and pagination.

    **Filter Options:**
    - **Format**: Use `key=value` query parameters (e.g., `?name=exam`)
    - **OR condition**: Use comma-separated values (e.g., `?name=test1,test2`)

    **Search Keys:**
    - `name`: Search in test name (text search)

    **Examples:**
    - Simple filter: `?name=exam`
    - Multiple filters: `?name=exam&description=test`
    - OR condition: `?name=exam1,exam2,exam3`

    Requires permission: tests::read
    """
    request_params = dict(request.query_params)

    # Determine if user has elevated access (Admin or Editor — has tests::* or *::*)
    is_elevated = permission_service.check_permission(
        db, user, "tests::*"
    ) or permission_service.check_permission(db, user, "*::*")

    allowed_category_ids = None
    if not is_elevated:
        access_records = user_category_access_repo.get_categories_for_user(db, user.id)
        allowed_category_ids = [str(a.category_id) for a in access_records]

    tests, total = category_service.get_all_tests(
        db,
        page=page,
        page_size=page_size,
        request_params=request_params,
        allowed_category_ids=allowed_category_ids,
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
        403: {
            "description": "Permission denied",
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
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_TESTS, "GET")
    ),
):
    """
    Get a specific test by ID.

    - **test_id**: UUID of the test

    Requires permission: tests::read
    """
    test = category_service.get_test_by_id_only(db, test_id)

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test with ID {test_id} not found",
        )

    return TestDetailResponse(data=test, meta={})


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
    },
)
def submit_test_submissions(
    test_id: str = Path(
        ...,
        description="Test ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    bulk_data: SubmissionBulkCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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

    # Enforce assignment check for non-elevated users (not Admin or Editor)
    is_elevated = permission_service.check_permission(
        db, current_user, "tests::*"
    ) or permission_service.check_permission(db, current_user, "*::*")

    if not is_elevated:
        has_assignment = user_test_assignment_repo.check_user_has_access(
            db, current_user.id, UUID(test_id)
        )
        if not has_assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have an active assignment for this test",
            )

    submissions = submission_service.submit_submissions_bulk(
        db, current_user.id, bulk_data.submissions
    )
    return SubmissionListResponse(data=submissions, meta={})


@router.get(
    "/{test_id}/submit/{submission_history_id}",
    response_model=SubmissionHistoryResponse,
    summary="Get test submission result",
    description="Get the result of a specific submission history for a test (requires authentication)",
    responses={
        200: {"description": "Submission result"},
        401: {"description": "Unauthorized access", "model": ErrorResponse},
        404: {"description": "Submission not found", "model": ErrorResponse},
    },
)
def get_test_submission_result(
    test_id: str = Path(..., description="Test ID"),
    submission_history_id: str = Path(..., description="Submission History ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the result of a specific submission history record.

    - **test_id**: Test UUID
    - **submission_history_id**: Submission History UUID

    Requires authentication token in header: `Authorization: Bearer <token>`
    """
    try:
        sh_uuid = UUID(submission_history_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid submission history ID format: {submission_history_id}",
        )

    result = submission_repo.get_submission_history_by_id(db, sh_uuid, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    return SubmissionHistoryResponse(data=result, meta={})


@router.post(
    "",
    response_model=TestDetailResponse,
    summary="Create a new test",
    description="Create a new test (requires permission)",
    responses={
        200: {
            "description": "Test created",
        },
        400: {
            "description": "Test name already exists or category not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def create_test(
    test_data: TestCreateRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_TESTS, "POST")
    ),
):
    """
    Create a new test.

    - **name**: Test name (1-100 characters)
    - **category_id**: Category ID

    Requires permission: tests::create
    """
    # Check if category exists
    from app.models.categories import Category

    category = (
        db.query(Category)
        .filter(Category.id == test_data.category_id, Category.deleted_at.is_(None))
        .first()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with ID {test_data.category_id} not found",
        )

    # Check if test name already exists in the same category (exact match)
    from app.models.tests import Test

    existing_test = (
        db.query(Test)
        .filter(
            Test.name == test_data.name,
            Test.category_id == test_data.category_id,
            Test.deleted_at.is_(None),
        )
        .first()
    )
    if existing_test:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Test with name '{test_data.name}' already exists in this category",
        )

    test = category_service.create_test(
        db,
        test_data.name,
        str(test_data.category_id),
        test_data.time_limit,
        test_data.description,
    )
    if not test:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create test",
        )

    return TestDetailResponse(data=test, meta={})


@router.put(
    "/{test_id}",
    response_model=TestDetailResponse,
    summary="Update a test",
    description="Update a test by ID (requires permission)",
    responses={
        200: {
            "description": "Test updated",
        },
        404: {
            "description": "Test not found",
            "model": ErrorResponse,
        },
        400: {
            "description": "Test name already exists",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def update_test(
    test_id: str = Path(
        ...,
        description="Test ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    test_data: TestUpdateRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_TESTS, "PUT")
    ),
):
    """
    Update a test by ID.

    - **test_id**: UUID of the test
    - **name**: New test name (1-100 characters)

    Requires permission: tests::update
    """
    # Check if test exists
    existing_test = category_service.get_test_by_id_only(db, test_id)
    if not existing_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test with ID {test_id} not found",
        )

    # Check if new name already exists in the same category (excluding current test, exact match)
    from app.models.tests import Test

    test_obj = (
        db.query(Test).filter(Test.id == test_id, Test.deleted_at.is_(None)).first()
    )

    existing_test = (
        db.query(Test)
        .filter(
            Test.name == test_data.name,
            Test.category_id == test_obj.category_id,
            Test.id != test_id,
            Test.deleted_at.is_(None),
        )
        .first()
    )
    if existing_test:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Test with name '{test_data.name}' already exists in this category",
        )

    test = category_service.update_test(
        db, test_id, test_data.name, test_data.time_limit, test_data.description
    )
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test with ID {test_id} not found",
        )

    return TestDetailResponse(data=test, meta={})


@router.delete(
    "/{test_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a test",
    description="Delete a test by ID (soft delete, requires permission)",
    responses={
        200: {
            "description": "Test deleted successfully",
        },
        404: {
            "description": "Test not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def delete_test(
    test_id: str = Path(
        ...,
        description="Test ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_TESTS, "DELETE")
    ),
):
    """
    Delete a test by ID (soft delete).

    - **test_id**: UUID of the test

    Requires permission: tests::delete
    """
    deleted = category_service.delete_test(db, test_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test with ID {test_id} not found",
        )

    return {"message": "Test deleted successfully"}
