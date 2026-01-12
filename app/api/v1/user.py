# app/api/v1/user.py
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.schemas.user import UserOut, UserListResponse, UserResponse
from app.schemas.http_response import ErrorResponse
from app.services import user_service
from app.db.session import get_db
from app.utils.search_pagination import get_pagination_meta
from app.constants import ERROR_USER_NOT_FOUND

router = APIRouter()


@router.get(
    "",
    response_model=UserListResponse,
    summary="Get all users",
    description="Get list of all users in the system with optional filtering and pagination. Supports both single filter (key, value) and multiple filters (filter-key-1, filter-value-1, ...). For comma-separated values, use OR condition.",
    responses={
        200: {
            "description": "List of users",
        }
    }
)
def read_users(
    request: Request,
    key: Optional[str] = Query(None, description="Search key: full_name, user_id, email, or phone (legacy format)"),
    value: Optional[str] = Query(None, description="Search value (legacy format)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    filter_key_1: Optional[str] = Query(None, alias="filter-key-1", description="First filter key (e.g., full_name, user_id, email, phone)"),
    filter_value_1: Optional[str] = Query(None, alias="filter-value-1", description="First filter value (supports comma-separated for OR)"),
    filter_key_2: Optional[str] = Query(None, alias="filter-key-2", description="Second filter key"),
    filter_value_2: Optional[str] = Query(None, alias="filter-value-2", description="Second filter value"),
    filter_key_3: Optional[str] = Query(None, alias="filter-key-3", description="Third filter key"),
    filter_value_3: Optional[str] = Query(None, alias="filter-value-3", description="Third filter value"),
    db: Session = Depends(get_db)
):
    """
    Get list of all users with optional filtering and pagination.
    
    **Filter Options:**
    - **Legacy format**: Use `key` and `value` parameters for single filter
    - **Multiple filters**: Use `filter-key-1`, `filter-value-1`, `filter-key-2`, `filter-value-2`, etc.
    - **OR condition**: Use comma-separated values in filter-value (e.g., `filter-value-1=user1,user2,user3`)
    
    **Search Keys:**
    - `full_name`: Search in user full name (text search)
    - `user_id`: Search in user_id (editable identifier, text search)
    - `email`: Search in email (text search)
    - `phone`: Search in phone number (text search)
    
    **Examples:**
    - Single filter: `?key=full_name&value=John`
    - Multiple filters: `?filter-key-1=full_name&filter-value-1=John&filter-key-2=email&filter-value-2=example`
    - OR condition: `?filter-key-1=user_id&filter-value-1=user1,user2,user3`
    
    This endpoint does not require authentication.
    """
    request_params = dict(request.query_params)
    users, total = user_service.list_users(
        db, search_key=key, search_value=value, page=page, page_size=page_size, request_params=request_params
    )
    meta = get_pagination_meta(total, page, page_size)
    return UserListResponse(data=users, meta=meta)


@router.get(
    "/{user_identifier}",
    response_model=UserResponse,
    summary="Get user information by ID or user_id",
    description="Get detailed information of a user by UUID ID or user_id (editable identifier) (public endpoint)",
    responses={
        200: {
            "description": "User information",
        },
        404: {
            "description": "User not found",
            "model": ErrorResponse,
        }
    }
)
def read_user(user_identifier: str, db: Session = Depends(get_db)):
    """
    Get user information by UUID ID or user_id (editable identifier).
    
    - **user_identifier**: UUID ID or user_id (6-character string) of the user to get information for
    
    This endpoint does not require authentication.
    """
    # Try to parse as UUID first
    try:
        user_uuid = UUID(user_identifier)
        user = user_service.get_user(db, user_uuid)
    except ValueError:
        # If not a valid UUID, try as user_id (editable identifier)
        user = user_service.get_user_by_user_id(db, user_identifier)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_FOUND)
    return UserResponse(data=user, meta={})
