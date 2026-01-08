# app/api/v1/category.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.question import (
    CategoryDetailListResponse,
    CategoryDetailResponse,
    QuestionSetDetailListResponse,
    QuestionSetDetailResponse,
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
    "/{category_id}/question-sets",
    response_model=QuestionSetDetailListResponse,
    summary="Get question sets by category",
    description="Get all question sets of a specific category with optional name search and pagination",
    responses={
        200: {
            "description": "List of question sets",
        },
        404: {
            "description": "Category not found",
            "model": ErrorResponse,
        },
    },
)
def get_question_sets_by_category(
    category_id: str = Path(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    key: Optional[str] = Query(None, description="Search key: name"),
    value: Optional[str] = Query(
        None, description="Search value for question set name"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
):
    """
    Get all question sets of a specific category with optional filtering and pagination.

    - **category_id**: UUID of the category
    - **key**: Search key (only "name" is supported)
    - **value**: Value to search for in question set name
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10, max: 100)

    This endpoint does not require authentication.
    """
    question_sets, total = category_service.get_question_sets_by_category_id(
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

    return QuestionSetDetailListResponse(data=question_sets, meta=meta)


@router.get(
    "/{category_id}/question-sets/{question_set_id}",
    response_model=QuestionSetDetailResponse,
    summary="Get question set by ID",
    description="Get a specific question set by category ID and question set ID",
    responses={
        200: {
            "description": "Question set details",
        },
        404: {
            "description": "Category or question set not found",
            "model": ErrorResponse,
        },
    },
)
def get_question_set_by_id(
    category_id: str = Path(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    question_set_id: str = Path(
        ...,
        description="Question set ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    db: Session = Depends(get_db),
):
    """
    Get a specific question set by category ID and question set ID.

    - **category_id**: UUID of the category
    - **question_set_id**: UUID of the question set

    This endpoint does not require authentication.
    """
    question_set = category_service.get_question_set_by_id(
        db, category_id, question_set_id
    )

    if not question_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question set with ID {question_set_id} not found in category {category_id}",
        )

    return QuestionSetDetailResponse(data=question_set, meta={})


@router.get(
    "/{category_id}/question-sets/{question_set_id}/questions",
    response_model=QuestionListResponse,
    summary="Get questions by question set",
    description="Get all questions of a specific question set with optional filtering and pagination",
    responses={
        200: {
            "description": "List of questions with answers",
        },
        404: {
            "description": "Category, question set, or questions not found",
            "model": ErrorResponse,
        },
    },
)
def get_questions_by_question_set(
    category_id: str = Path(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    question_set_id: str = Path(
        ...,
        description="Question set ID",
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
    Get all questions of a specific question set with optional filtering and pagination.

    - **category_id**: UUID of the category
    - **question_set_id**: UUID of the question set
    - **key**: Search key (content or created_at)
    - **value**: Value to search for
    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10, max: 100)

    This endpoint does not require authentication.
    """
    questions, total = question_service.get_questions_by_category_and_set_id(
        db,
        category_id,
        question_set_id,
        search_key=key,
        search_value=value,
        page=page,
        page_size=page_size,
    )

    # If no results and first page, verify category and question set exist
    if total == 0 and page == 1:
        question_set = category_service.get_question_set_by_id(
            db, category_id, question_set_id
        )
        if not question_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question set with ID {question_set_id} not found in category {category_id}",
            )

    meta = get_pagination_meta(total, page, page_size)

    return QuestionListResponse(data=questions, meta=meta)
