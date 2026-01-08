# app/api/v1/category.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.question import (
    CategoryDetailListResponse, CategoryDetailResponse
)
from app.schemas.http_response import ErrorResponse
from app.services import category_service
from app.db.session import get_db

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
    }
)
def get_all_categories(
    key: Optional[str] = Query(None, description="Search key: name"),
    value: Optional[str] = Query(None, description="Search value for category name"),
    db: Session = Depends(get_db)
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
        }
    }
)
def get_category_by_id(
    category_id: str = Path(..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"),
    db: Session = Depends(get_db)
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
            detail=f"Category with ID {category_id} not found"
        )
    
    return CategoryDetailResponse(data=category, meta={})
