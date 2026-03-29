# app/api/v1/user_tests.py
from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies.permissions import require_namespace_permission
from app.constants.permissions import PERMISSION_NAMESPACE_USER_TESTS
from app.db.session import get_db
from app.models.users import User
from app.schemas.http_response import ErrorResponse
from app.schemas.question import QuestionWithAnswersListResponse
from app.schemas.user_test_assignment import (
    UserTestAssignmentListResponse,
)
from app.services import user_test_assignment_service
from app.utils.search_pagination import get_pagination_meta

router = APIRouter()


@router.get(
    "",
    response_model=UserTestAssignmentListResponse,
    summary="Get my assigned tests",
    description="Get all tests assigned to the current user",
    responses={
        200: {"description": "List of assigned tests"},
        401: {"description": "Unauthorized", "model": ErrorResponse},
    },
)
def get_my_assigned_tests(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_USER_TESTS, "GET")
    ),
):
    """
    Get all tests assigned to the current user.

    Returns tests with details including name, description, time limit, and question count.

    Requires permission: user_tests::read
    """
    request_params = dict(request.query_params)
    assignments, total = user_test_assignment_service.get_user_assignments(
        db,
        current_user.id,
        page=page,
        page_size=page_size,
        request_params=request_params,
    )

    meta = get_pagination_meta(total, page, page_size)
    return UserTestAssignmentListResponse(data=assignments, meta=meta)


@router.get(
    "/{test_id}/questions",
    response_model=QuestionWithAnswersListResponse,
    summary="Get questions for an assigned test",
    description="Get all questions for a test that the user has access to",
    responses={
        200: {"description": "List of questions"},
        403: {"description": "Access denied - not assigned to this test", "model": ErrorResponse},
        404: {"description": "Test not found", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
    },
)
def get_test_questions(
    request: Request,
    test_id: str = Path(..., description="Test ID"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_USER_TESTS, "GET")
    ),
):
    """
    Get questions for a test that the user has been assigned to.

    - Checks if the user has access to this test (is assigned)
    - Returns 403 if user doesn't have access
    - Returns questions with answers for the test

    Requires permission: user_tests::read
    """
    request_params = dict(request.query_params)
    questions, total = user_test_assignment_service.get_test_questions_for_user(
        db,
        current_user.id,
        test_id,
        page=page,
        page_size=page_size,
        request_params=request_params,
    )

    meta = get_pagination_meta(total, page, page_size)
    return QuestionWithAnswersListResponse(data=questions, meta=meta)
