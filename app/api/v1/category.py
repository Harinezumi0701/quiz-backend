# app/api/v1/category.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.question import (
    CategoryDetailListResponse,
    CategoryDetailResponse,
    TestDetailListResponse,
    TestDetailResponse,
    QuestionListResponse,
)
from app.schemas.http_response import ErrorResponse
from app.services import category_service, question_service
from app.db.session import get_db
from app.utils.search_pagination import get_pagination_meta

router = APIRouter()


@router.get(
    "/",
    response_model=CategoryDetailListResponse,
    summary="Get all categories",
    description="Get list of all categories with optional name search",
    responses={
        200: {
            "description": "List of categories",
        }
    },
)
def get_all_categories(
    key: Optional[str] = Query(None, description="Search key: name"),
    value: Optional[str] = Query(None, description="Search value for category name"),
    db: Session = Depends(get_db),
):
    """
    Get all categories with optional name search.

    - **key**: Search key (only "name" is supported)
    - **value**: Value to search for in category name

    This endpoint does not require authentication.
    """
    categories = category_service.get_all_categories_with_search(
        db, search_key=key, search_value=value
    )

    return CategoryDetailListResponse(data=categories, meta={})


@router.get(
    "/{category_id}",
    response_model=CategoryDetailResponse,
    summary="Get category by ID",
    description="Get a specific category by ID",
    responses={
        200: {
            "description": "Category details",
        },
        404: {
            "description": "Category not found",
            "model": ErrorResponse,
        },
    },
)
def get_category_by_id(
    category_id: str = Path(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    db: Session = Depends(get_db),
):
    """
    Get a specific category by ID.

    - **category_id**: UUID of the category

    This endpoint does not require authentication.
    """
    category = category_service.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    return CategoryDetailResponse(data=category, meta={})


@router.get(
    "/{category_id}/tests",
    response_model=TestDetailListResponse,
    summary="Get tests by category",
    description="Get all tests of a specific category with optional name search and pagination",
    responses={
        200: {
            "description": "List of tests",
        },
        404: {
            "description": "Category not found",
            "model": ErrorResponse,
        },
    },
)
def get_tests_by_category(
    category_id: str = Path(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    key: Optional[str] = Query(None, description="Search key: name"),
    value: Optional[str] = Query(
        None, description="Search value for test name"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
):
    """
    Get all tests of a specific category with optional filtering and pagination.

    - **category_id**: UUID of the category
    - **key**: Search key (only "name" is supported)
    - **value**: Value to search for in test name
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10, max: 100)

    This endpoint does not require authentication.
    """
    tests, total = category_service.get_tests_by_category_id(
        db,
        category_id,
        search_key=key,
        search_value=value,
        page=page,
        page_size=page_size,
    )

    # If no results and first page, verify category exists
    if total == 0 and page == 1:
        category = category_service.get_category_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found",
            )

    meta = get_pagination_meta(total, page, page_size)

    return TestDetailListResponse(data=tests, meta=meta)


@router.get(
    "/{category_id}/tests/{test_id}",
    response_model=TestDetailResponse,
    summary="Get test by ID",
    description="Get a specific test by category ID and test ID",
    responses={
        200: {
            "description": "Test details",
        },
        404: {
            "description": "Category or test not found",
            "model": ErrorResponse,
        },
    },
)
def get_test_by_id(
    category_id: str = Path(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    test_id: str = Path(
        ...,
        description="Test ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    db: Session = Depends(get_db),
):
    """
    Get a specific test by category ID and test ID.

    - **category_id**: UUID of the category
    - **test_id**: UUID of the test

    This endpoint does not require authentication.
    """
    test = category_service.get_test_by_id(
        db, category_id, test_id
    )

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test with ID {test_id} not found in category {category_id}",
        )

    return TestDetailResponse(data=test, meta={})


@router.get(
    "/{category_id}/tests/{test_id}/questions",
    response_model=QuestionListResponse,
    summary="Get questions by test",
    description="Get all questions of a specific test with optional filtering and pagination",
    responses={
        200: {
            "description": "List of questions with answers",
        },
        404: {
            "description": "Category, test, or questions not found",
            "model": ErrorResponse,
        },
    },
)
def get_questions_by_test(
    category_id: str = Path(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    test_id: str = Path(
        ...,
        description="Test ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    key: Optional[str] = Query(
        None, description="Search key: content or created_at"
    ),
    value: Optional[str] = Query(None, description="Search value"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
):
    """
    Get all questions of a specific test with optional filtering and pagination.

    - **category_id**: UUID of the category
    - **test_id**: UUID of the test
    - **key**: Search key (content or created_at)
    - **value**: Value to search for
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10, max: 100)

    This endpoint does not require authentication.
    """
    questions, total = question_service.get_questions_by_category_and_test_id(
        db,
        category_id,
        test_id,
        search_key=key,
        search_value=value,
        page=page,
        page_size=page_size,
    )

    # If no results and first page, verify category and test exist
    if total == 0 and page == 1:
        test = category_service.get_test_by_id(
            db, category_id, test_id
        )
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test with ID {test_id} not found in category {category_id}",
            )

    meta = get_pagination_meta(total, page, page_size)

    return QuestionListResponse(data=questions, meta=meta)
