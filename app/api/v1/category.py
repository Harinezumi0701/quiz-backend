# app/api/v1/category.py

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

from app.api.dependencies.permissions import require_namespace_permission
from app.constants.permissions import (
    PERMISSION_NAMESPACE_CATEGORIES,
)
from app.db.session import get_db
from app.models.users import User
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryDetailListResponse,
    CategoryDetailResponse,
    CategoryUpdateRequest,
)
from app.schemas.http_response import ErrorResponse
from app.services import category_service
from app.utils.search_pagination import get_pagination_meta

router = APIRouter()


@router.get(
    "",
    response_model=CategoryDetailListResponse,
    summary="Get all categories",
    description="Get list of all categories with optional name search and pagination. Supports standard query parameters for filtering (key=value). For comma-separated values, use OR condition.",
    responses={
        200: {
            "description": "List of categories",
        }
    },
)
def get_all_categories(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_CATEGORIES, "GET")
    ),
):
    """
    Get all categories with optional name search and pagination.

    **Filter Options:**
    - **Format**: Use `key=value` query parameters (e.g., `?name=math`)
    - **OR condition**: Use comma-separated values (e.g., `?name=cat1,cat2`)

    **Search Keys:**
    - `name`: Search in category name (text search)

    **Examples:**
    - Simple filter: `?name=math`
    - Multiple filters: `?name=math&description=science` (if description search is supported)
    - OR condition: `?name=math,science,history`

    Requires permission: categories::read
    """
    request_params = dict(request.query_params)
    categories, total = category_service.get_all_categories_with_search(
        db,
        page=page,
        page_size=page_size,
        request_params=request_params,
    )


    meta = get_pagination_meta(total, page, page_size)

    return CategoryDetailListResponse(data=categories, meta=meta)


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
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_CATEGORIES, "GET")
    ),
):
    """
    Get a specific category by ID.

    - **category_id**: UUID of the category

    Requires permission: categories::read
    """
    category = category_service.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    return CategoryDetailResponse(data=category, meta={})


@router.post(
    "",
    response_model=CategoryDetailResponse,
    summary="Create a new category",
    description="Create a new category (requires permission)",
    responses={
        200: {
            "description": "Category created",
        },
        400: {
            "description": "Category name already exists",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def create_category(
    category_data: CategoryCreateRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_CATEGORIES, "POST")
    ),
):
    """
    Create a new category.

    - **name**: Category name (1-100 characters)

    Requires permission: categories::create
    """
    # Check if category name already exists (exact match)
    from app.models.categories import Category

    existing_category = (
        db.query(Category)
        .filter(Category.name == category_data.name, Category.deleted_at.is_(None))
        .first()
    )
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category_data.name}' already exists",
        )

    category = category_service.create_category(db, category_data.name)
    return CategoryDetailResponse(data=category, meta={})


@router.put(
    "/{category_id}",
    response_model=CategoryDetailResponse,
    summary="Update a category",
    description="Update a category by ID (requires permission)",
    responses={
        200: {
            "description": "Category updated",
        },
        404: {
            "description": "Category not found",
            "model": ErrorResponse,
        },
        400: {
            "description": "Category name already exists",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def update_category(
    category_id: str = Path(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    category_data: CategoryUpdateRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_CATEGORIES, "PUT")
    ),
):
    """
    Update a category by ID.

    - **category_id**: UUID of the category
    - **name**: New category name (1-100 characters)

    Requires permission: categories::update
    """
    # Check if category exists
    existing_category = category_service.get_category_by_id(db, category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    # Check if new name already exists (excluding current category, exact match)
    from app.models.categories import Category

    existing_category = (
        db.query(Category)
        .filter(
            Category.name == category_data.name,
            Category.id != category_id,
            Category.deleted_at.is_(None),
        )
        .first()
    )
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category_data.name}' already exists",
        )

    category = category_service.update_category(db, category_id, category_data.name)
    return CategoryDetailResponse(data=category, meta={})


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a category",
    description="Delete a category by ID (soft delete, requires permission)",
    responses={
        200: {
            "description": "Category deleted successfully",
        },
        404: {
            "description": "Category not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def delete_category(
    category_id: str = Path(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_CATEGORIES, "DELETE")
    ),
):
    """
    Delete a category by ID (soft delete).

    - **category_id**: UUID of the category

    Requires permission: categories::delete
    """
    deleted = category_service.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    return {"message": "Category deleted successfully"}
