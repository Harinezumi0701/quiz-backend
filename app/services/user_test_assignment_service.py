# app/services/user_test_assignment_service.py
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status
from app.repository import user_test_assignment_repo, question_repo


def get_user_assignments(
    db: Session,
    user_id: UUID,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """Get all test assignments for a user."""
    return user_test_assignment_repo.get_user_assignments(
        db, user_id, page=page, page_size=page_size, request_params=request_params
    )


def get_all_assignments(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """Get all test assignments (admin)."""
    return user_test_assignment_repo.get_all_assignments(
        db, page=page, page_size=page_size, request_params=request_params
    )


def check_user_has_access(
    db: Session,
    user_id: UUID,
    test_id: UUID,
) -> bool:
    """Check if user has access to a specific test."""
    return user_test_assignment_repo.check_user_has_access(db, user_id, test_id)


def get_test_questions_for_user(
    db: Session,
    user_id: UUID,
    test_id: str,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
):
    """
    Get questions for a test that the user has access to.

    Raises HTTPException if user doesn't have access.
    """
    # Check if user has access to this test
    has_access = user_test_assignment_repo.check_user_has_access(db, user_id, UUID(test_id))

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this test",
        )

    # Get questions for this test
    return question_repo.get_questions_by_test_id(
        db, test_id, page=page, page_size=page_size, request_params=request_params
    )


def create_assignment(
    db: Session,
    user_id: UUID,
    test_id: UUID,
    expires_at: Optional[datetime] = None,
) -> dict:
    """Create a new test assignment."""
    assignment = user_test_assignment_repo.create_assignment(
        db, user_id, test_id, expires_at
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User or test not found, or assignment already exists",
        )

    return assignment


def create_bulk_assignments(
    db: Session,
    user_ids: list[UUID],
    test_id: UUID,
    expires_at: Optional[datetime] = None,
) -> dict:
    """Create test assignments for multiple users."""
    created, skipped = user_test_assignment_repo.create_bulk_assignments(
        db, user_ids, test_id, expires_at
    )

    return {
        "created": created,
        "skipped": skipped,
        "total": len(user_ids),
    }


def delete_assignment(
    db: Session,
    assignment_id: UUID,
) -> bool:
    """Delete a test assignment."""
    deleted = user_test_assignment_repo.delete_assignment(db, assignment_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID {assignment_id} not found",
        )

    return deleted


def delete_assignment_by_user_and_test(
    db: Session,
    user_id: UUID,
    test_id: UUID,
) -> bool:
    """Delete a test assignment by user and test."""
    deleted = user_test_assignment_repo.delete_assignment_by_user_and_test(
        db, user_id, test_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    return deleted
