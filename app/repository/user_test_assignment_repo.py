# app/repository/user_test_assignment_repo.py
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from typing import Optional, Tuple, Dict, Any
from app.models.user_test_assignments import UserTestAssignment
from app.models.tests import Test
from app.models.users import User
from app.models.questions import Question
from app.utils.datetime_utils import datetime_to_timestamp
from app.utils.search_pagination import paginate_query_with_multiple_filters


def get_user_assignments(
    db: Session,
    user_id: UUID,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all test assignments for a specific user.

    Args:
        db: Database session
        user_id: User UUID
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for filters

    Returns:
        Tuple of (assignments list with test details, total count)
    """
    query = (
        db.query(UserTestAssignment)
        .options(joinedload(UserTestAssignment.test))
        .filter(
            UserTestAssignment.user_id == user_id,
            UserTestAssignment.deleted_at.is_(None),
        )
        .order_by(UserTestAssignment.assigned_at.desc())
    )

    search_config = {
        "test_id": {
            "column": UserTestAssignment.test_id,
            "type": "exact",
        },
    }

    paginated_query, total = paginate_query_with_multiple_filters(
        query,
        request_params=request_params or {},
        search_config=search_config,
        page=page,
        page_size=page_size,
    )

    assignments = paginated_query.all()

    result = []
    for assignment in assignments:
        test = assignment.test
        if test and test.deleted_at is None:
            question_count = (
                db.query(Question)
                .filter(Question.test_id == test.id, Question.deleted_at.is_(None))
                .count()
            )
            result.append(
                {
                    "id": assignment.id,
                    "test_id": assignment.test_id,
                    "test_name": test.name,
                    "test_description": test.description,
                    "test_time_limit": test.time_limit,
                    "question_count": question_count,
                    "category_id": test.category_id,
                    "assigned_at": datetime_to_timestamp(assignment.assigned_at),
                    "expires_at": datetime_to_timestamp(assignment.expires_at) if assignment.expires_at else None,
                }
            )

    return result, total


def get_assignment_by_user_and_test(
    db: Session,
    user_id: UUID,
    test_id: UUID,
) -> Optional[dict]:
    """
    Get a specific assignment for a user and test.

    Args:
        db: Database session
        user_id: User UUID
        test_id: Test UUID

    Returns:
        Assignment dict or None if not found
    """
    assignment = (
        db.query(UserTestAssignment)
        .options(joinedload(UserTestAssignment.test))
        .filter(
            UserTestAssignment.user_id == user_id,
            UserTestAssignment.test_id == test_id,
            UserTestAssignment.deleted_at.is_(None),
        )
        .first()
    )

    if not assignment:
        return None

    test = assignment.test
    if not test or test.deleted_at is not None:
        return None

    return {
        "id": assignment.id,
        "user_id": assignment.user_id,
        "test_id": assignment.test_id,
        "assigned_at": datetime_to_timestamp(assignment.assigned_at),
        "expires_at": datetime_to_timestamp(assignment.expires_at) if assignment.expires_at else None,
    }


def check_user_has_access(
    db: Session,
    user_id: UUID,
    test_id: UUID,
) -> bool:
    """
    Check if a user has access to a specific test.

    Args:
        db: Database session
        user_id: User UUID
        test_id: Test UUID

    Returns:
        True if user has access, False otherwise
    """
    assignment = (
        db.query(UserTestAssignment)
        .filter(
            UserTestAssignment.user_id == user_id,
            UserTestAssignment.test_id == test_id,
            UserTestAssignment.deleted_at.is_(None),
        )
        .first()
    )

    if not assignment:
        return False

    # Check if assignment has expired
    if assignment.expires_at and assignment.expires_at < datetime.now(timezone.utc):
        return False

    return True


def get_all_assignments(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all test assignments with optional filtering and pagination.

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for filters

    Returns:
        Tuple of (assignments list, total count)
    """
    query = (
        db.query(UserTestAssignment)
        .options(
            joinedload(UserTestAssignment.test),
            joinedload(UserTestAssignment.user),
        )
        .filter(UserTestAssignment.deleted_at.is_(None))
        .order_by(UserTestAssignment.assigned_at.desc())
    )

    search_config = {
        "user_id": {
            "column": UserTestAssignment.user_id,
            "type": "exact",
        },
        "test_id": {
            "column": UserTestAssignment.test_id,
            "type": "exact",
        },
    }

    paginated_query, total = paginate_query_with_multiple_filters(
        query,
        request_params=request_params or {},
        search_config=search_config,
        page=page,
        page_size=page_size,
    )

    assignments = paginated_query.all()

    result = []
    for assignment in assignments:
        test = assignment.test
        user = assignment.user
        if test and test.deleted_at is None and user and user.deleted_at is None:
            result.append(
                {
                    "id": assignment.id,
                    "user_id": assignment.user_id,
                    "user_email": user.email,
                    "user_full_name": user.full_name,
                    "test_id": assignment.test_id,
                    "test_name": test.name,
                    "assigned_at": datetime_to_timestamp(assignment.assigned_at),
                    "expires_at": datetime_to_timestamp(assignment.expires_at) if assignment.expires_at else None,
                }
            )

    return result, total


def create_assignment(
    db: Session,
    user_id: UUID,
    test_id: UUID,
    expires_at: Optional[datetime] = None,
) -> Optional[dict]:
    """
    Create a new test assignment for a user.

    Args:
        db: Database session
        user_id: User UUID
        test_id: Test UUID
        expires_at: Optional expiration datetime

    Returns:
        Assignment dict or None if user/test not found or already assigned
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        return None

    # Verify test exists
    test = db.query(Test).filter(Test.id == test_id, Test.deleted_at.is_(None)).first()
    if not test:
        return None

    # Check if assignment already exists
    existing = (
        db.query(UserTestAssignment)
        .filter(
            UserTestAssignment.user_id == user_id,
            UserTestAssignment.test_id == test_id,
            UserTestAssignment.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        return None  # Already assigned

    assignment = UserTestAssignment(
        user_id=user_id,
        test_id=test_id,
        expires_at=expires_at,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "id": assignment.id,
        "user_id": assignment.user_id,
        "test_id": assignment.test_id,
        "assigned_at": datetime_to_timestamp(assignment.assigned_at),
        "expires_at": datetime_to_timestamp(assignment.expires_at) if assignment.expires_at else None,
    }


def create_bulk_assignments(
    db: Session,
    user_ids: list[UUID],
    test_id: UUID,
    expires_at: Optional[datetime] = None,
) -> Tuple[int, int]:
    """
    Create test assignments for multiple users.

    Args:
        db: Database session
        user_ids: List of User UUIDs
        test_id: Test UUID
        expires_at: Optional expiration datetime

    Returns:
        Tuple of (created count, skipped count)
    """
    # Verify test exists
    test = db.query(Test).filter(Test.id == test_id, Test.deleted_at.is_(None)).first()
    if not test:
        return 0, len(user_ids)

    created = 0
    skipped = 0

    for user_id in user_ids:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
        if not user:
            skipped += 1
            continue

        # Check if assignment already exists
        existing = (
            db.query(UserTestAssignment)
            .filter(
                UserTestAssignment.user_id == user_id,
                UserTestAssignment.test_id == test_id,
                UserTestAssignment.deleted_at.is_(None),
            )
            .first()
        )
        if existing:
            skipped += 1
            continue

        assignment = UserTestAssignment(
            user_id=user_id,
            test_id=test_id,
            expires_at=expires_at,
        )
        db.add(assignment)
        created += 1

    db.commit()
    return created, skipped


def delete_assignment(
    db: Session,
    assignment_id: UUID,
) -> bool:
    """
    Soft delete a test assignment.

    Args:
        db: Database session
        assignment_id: Assignment UUID

    Returns:
        True if deleted, False if not found
    """
    assignment = (
        db.query(UserTestAssignment)
        .filter(
            UserTestAssignment.id == assignment_id,
            UserTestAssignment.deleted_at.is_(None),
        )
        .first()
    )

    if not assignment:
        return False

    assignment.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True


def delete_assignment_by_user_and_test(
    db: Session,
    user_id: UUID,
    test_id: UUID,
) -> bool:
    """
    Soft delete a test assignment by user and test.

    Args:
        db: Database session
        user_id: User UUID
        test_id: Test UUID

    Returns:
        True if deleted, False if not found
    """
    assignment = (
        db.query(UserTestAssignment)
        .filter(
            UserTestAssignment.user_id == user_id,
            UserTestAssignment.test_id == test_id,
            UserTestAssignment.deleted_at.is_(None),
        )
        .first()
    )

    if not assignment:
        return False

    assignment.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
