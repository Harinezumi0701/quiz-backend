# app/api/v1/test_assignments.py
from datetime import datetime, timezone
from fastapi import APIRouter, Body, Depends, Path, Query, Request, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.user_test_assignment import (
    UserTestAssignmentAdminListResponse,
    UserTestAssignmentResponse,
    UserTestAssignmentCreateRequest,
    BulkAssignmentCreateRequest,
    BulkAssignmentCreateResponse,
)
from app.schemas.http_response import ErrorResponse
from app.services import user_test_assignment_service
from app.db.session import get_db
from app.utils.search_pagination import get_pagination_meta
from app.api.dependencies.permissions import require_namespace_permission
from app.models.users import User
from app.constants.permissions import PERMISSION_NAMESPACE_USER_TESTS

router = APIRouter()


@router.get(
    "",
    response_model=UserTestAssignmentAdminListResponse,
    summary="Get all test assignments (Admin)",
    description="Get all test assignments with optional filtering and pagination",
    responses={
        200: {"description": "List of test assignments"},
        403: {"description": "Permission denied", "model": ErrorResponse},
    },
)
def get_all_assignments(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_USER_TESTS, "GET")
    ),
):
    """
    Get all test assignments (admin view).

    **Filter Options:**
    - `user_id`: Filter by user ID
    - `test_id`: Filter by test ID

    Requires permission: user_tests::read (admin-level)
    """
    request_params = dict(request.query_params)
    assignments, total = user_test_assignment_service.get_all_assignments(
        db,
        page=page,
        page_size=page_size,
        request_params=request_params,
    )

    meta = get_pagination_meta(total, page, page_size)
    return UserTestAssignmentAdminListResponse(data=assignments, meta=meta)


@router.post(
    "",
    response_model=UserTestAssignmentResponse,
    summary="Create a test assignment",
    description="Assign a test to a user",
    responses={
        200: {"description": "Assignment created"},
        400: {"description": "User or test not found, or already assigned", "model": ErrorResponse},
        403: {"description": "Permission denied", "model": ErrorResponse},
    },
)
def create_assignment(
    assignment_data: UserTestAssignmentCreateRequest = Body(...),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_USER_TESTS, "POST")
    ),
):
    """
    Create a new test assignment.

    - **user_id**: User ID to assign the test to
    - **test_id**: Test ID to assign
    - **expires_at**: Optional expiration timestamp (null = never expires)

    Requires permission: user_tests::create
    """
    expires_at = None
    if assignment_data.expires_at:
        expires_at = datetime.fromtimestamp(assignment_data.expires_at, tz=timezone.utc)

    assignment = user_test_assignment_service.create_assignment(
        db,
        assignment_data.user_id,
        assignment_data.test_id,
        expires_at,
    )

    return UserTestAssignmentResponse(data=assignment, meta={})


@router.post(
    "/bulk",
    response_model=BulkAssignmentCreateResponse,
    summary="Create bulk test assignments",
    description="Assign a test to multiple users at once",
    responses={
        200: {"description": "Bulk assignments created"},
        403: {"description": "Permission denied", "model": ErrorResponse},
    },
)
def create_bulk_assignments(
    bulk_data: BulkAssignmentCreateRequest = Body(...),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_USER_TESTS, "POST")
    ),
):
    """
    Create test assignments for multiple users at once.

    - **user_ids**: List of User IDs to assign the test to
    - **test_id**: Test ID to assign
    - **expires_at**: Optional expiration timestamp (null = never expires)

    Returns the count of created and skipped assignments.

    Requires permission: user_tests::create
    """
    expires_at = None
    if bulk_data.expires_at:
        expires_at = datetime.fromtimestamp(bulk_data.expires_at, tz=timezone.utc)

    result = user_test_assignment_service.create_bulk_assignments(
        db,
        bulk_data.user_ids,
        bulk_data.test_id,
        expires_at,
    )

    return BulkAssignmentCreateResponse(data=result, meta={})


@router.delete(
    "/{assignment_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a test assignment",
    description="Remove a test assignment (soft delete)",
    responses={
        200: {"description": "Assignment deleted"},
        404: {"description": "Assignment not found", "model": ErrorResponse},
        403: {"description": "Permission denied", "model": ErrorResponse},
    },
)
def delete_assignment(
    assignment_id: UUID = Path(..., description="Assignment ID"),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_USER_TESTS, "DELETE")
    ),
):
    """
    Delete a test assignment by ID.

    Requires permission: user_tests::delete
    """
    user_test_assignment_service.delete_assignment(db, assignment_id)
    return {"message": "Assignment deleted successfully"}


@router.delete(
    "/user/{user_id}/test/{test_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a test assignment by user and test",
    description="Remove a test assignment by user ID and test ID (soft delete)",
    responses={
        200: {"description": "Assignment deleted"},
        404: {"description": "Assignment not found", "model": ErrorResponse},
        403: {"description": "Permission denied", "model": ErrorResponse},
    },
)
def delete_assignment_by_user_and_test(
    user_id: UUID = Path(..., description="User ID"),
    test_id: UUID = Path(..., description="Test ID"),
    db: Session = Depends(get_db),
    _user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_USER_TESTS, "DELETE")
    ),
):
    """
    Delete a test assignment by user ID and test ID.

    Requires permission: user_tests::delete
    """
    user_test_assignment_service.delete_assignment_by_user_and_test(db, user_id, test_id)
    return {"message": "Assignment deleted successfully"}
