# app/api/v1/category.py
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    status,
    Body,
)
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.category import (
    CategoryDetailListResponse,
    CategoryDetailResponse,
    CategoryCreateRequest,
    CategoryUpdateRequest,
)
from app.schemas.test import (
    TestDetailListResponse,
    TestDetailResponse,
)
from app.schemas.question import (
    QuestionListResponse,
)
from app.schemas.http_response import ErrorResponse
from app.services import category_service, question_service
from app.db.session import get_db
from app.utils.search_pagination import get_pagination_meta
from app.api.dependencies.permissions import require_namespace_permission
from app.models.users import User
from app.constants.permissions import (
    PERMISSION_NAMESPACE_CATEGORIES,
    PERMISSION_ACTION_READ,
    PERMISSION_ACTION_CREATE,
    PERMISSION_ACTION_UPDATE,
    PERMISSION_ACTION_DELETE,
)

router = APIRouter()


@router.get(
    "",
    response_model=CategoryDetailListResponse,
    summary="Get all categories",
    description="Get list of all categories with optional name search and pagination. Supports both single filter (key, value) and multiple filters (filter-key-1, filter-value-1, ...). For comma-separated values, use OR condition.",
    responses={
        200: {
            "description": "List of categories",
        }
    },
)
def get_all_categories(
    request: Request,
    key: Optional[str] = Query(None, description="Search key: name (legacy format)"),
    value: Optional[str] = Query(
        None, description="Search value for category name (legacy format)"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    filter_key_1: Optional[str] = Query(
        None, alias="filter-key-1", description="First filter key (e.g., name)"
    ),
    filter_value_1: Optional[str] = Query(
        None,
        alias="filter-value-1",
        description="First filter value (supports comma-separated for OR)",
    ),
    filter_key_2: Optional[str] = Query(
        None, alias="filter-key-2", description="Second filter key"
    ),
    filter_value_2: Optional[str] = Query(
        None, alias="filter-value-2", description="Second filter value"
    ),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_CATEGORIES, "GET")
    ),
):
    """
    Get all categories with optional name search and pagination.

    **Filter Options:**
    - **Legacy format**: Use `key` and `value` parameters for single filter
    - **Multiple filters**: Use `filter-key-1`, `filter-value-1`, `filter-key-2`, `filter-value-2`, etc.
    - **OR condition**: Use comma-separated values in filter-value (e.g., `filter-value-1=cat1,cat2,cat3`)

    **Search Keys:**
    - `name`: Search in category name (text search)

    **Examples:**
    - Single filter: `?key=name&value=math`
    - Multiple filters: `?filter-key-1=name&filter-value-1=math&filter-key-2=name&filter-value-2=science`
    - OR condition: `?filter-key-1=name&filter-value-1=math,science,history`

    Requires permission: categories::read
    """
    request_params = dict(request.query_params)
    categories, total = category_service.get_all_categories_with_search(
        db,
        search_key=key,
        search_value=value,
        page=page,
        page_size=page_size,
        request_params=request_params,
    )

    from app.utils.search_pagination import get_pagination_meta

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
    request: Request,
    category_id: str = Path(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    key: Optional[str] = Query(None, description="Search key: name (legacy format)"),
    value: Optional[str] = Query(
        None, description="Search value for test name (legacy format)"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    filter_key_1: Optional[str] = Query(
        None, alias="filter-key-1", description="First filter key (e.g., name)"
    ),
    filter_value_1: Optional[str] = Query(
        None,
        alias="filter-value-1",
        description="First filter value (supports comma-separated for OR)",
    ),
    filter_key_2: Optional[str] = Query(
        None, alias="filter-key-2", description="Second filter key"
    ),
    filter_value_2: Optional[str] = Query(
        None, alias="filter-value-2", description="Second filter value"
    ),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_CATEGORIES, "GET")
    ),
):
    """
    Get all tests of a specific category with optional filtering and pagination.

    **Filter Options:**
    - **Legacy format**: Use `key` and `value` parameters for single filter
    - **Multiple filters**: Use `filter-key-1`, `filter-value-1`, `filter-key-2`, `filter-value-2`, etc.
    - **OR condition**: Use comma-separated values in filter-value (e.g., `filter-value-1=test1,test2,test3`)

    **Search Keys:**
    - `name`: Search in test name (text search)

    **Examples:**
    - Single filter: `?key=name&value=exam`
    - Multiple filters: `?filter-key-1=name&filter-value-1=exam&filter-key-2=name&filter-value-2=test`

    Requires permission: categories::read
    """
    request_params = dict(request.query_params)
    tests, total = category_service.get_tests_by_category_id(
        db,
        category_id,
        search_key=key,
        search_value=value,
        page=page,
        page_size=page_size,
        request_params=request_params,
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
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_CATEGORIES, "GET")
    ),
):
    """
    Get a specific test by category ID and test ID.

    - **category_id**: UUID of the category
    - **test_id**: UUID of the test

    Requires permission: categories::read
    """
    test = category_service.get_test_by_id(db, category_id, test_id)

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
    request: Request,
    category_id: str = Path(
        ..., description="Category ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    test_id: str = Path(
        ...,
        description="Test ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    key: Optional[str] = Query(
        None, description="Search key: content or created_at (legacy format)"
    ),
    value: Optional[str] = Query(None, description="Search value (legacy format)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    filter_key_1: Optional[str] = Query(
        None,
        alias="filter-key-1",
        description="First filter key (e.g., content, created_at)",
    ),
    filter_value_1: Optional[str] = Query(
        None,
        alias="filter-value-1",
        description="First filter value (supports comma-separated for OR)",
    ),
    filter_key_2: Optional[str] = Query(
        None, alias="filter-key-2", description="Second filter key"
    ),
    filter_value_2: Optional[str] = Query(
        None, alias="filter-value-2", description="Second filter value"
    ),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_CATEGORIES, "GET")
    ),
):
    """
    Get all questions of a specific test with optional filtering and pagination.

    **Filter Options:**
    - **Legacy format**: Use `key` and `value` parameters for single filter
    - **Multiple filters**: Use `filter-key-1`, `filter-value-1`, `filter-key-2`, `filter-value-2`, etc.
    - **OR condition**: Use comma-separated values in filter-value (e.g., `filter-value-1=id1,id2,id3`)

    **Search Keys:**
    - `content`: Search in question content (text search)
    - `created_at`: Search by creation date (date search)

    **Examples:**
    - Single filter: `?key=content&value=test`
    - Multiple filters: `?filter-key-1=content&filter-value-1=test&filter-key-2=created_at&filter-value-2=2024-01-01`

    Requires permission: categories::read
    """
    request_params = dict(request.query_params)
    questions, total = question_service.get_questions_by_category_and_test_id(
        db,
        category_id,
        test_id,
        search_key=key,
        search_value=value,
        page=page,
        page_size=page_size,
        request_params=request_params,
    )

    # If no results and first page, verify category and test exist
    if total == 0 and page == 1:
        test = category_service.get_test_by_id(db, category_id, test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test with ID {test_id} not found in category {category_id}",
            )

    meta = get_pagination_meta(total, page, page_size)

    return QuestionListResponse(data=questions, meta=meta)


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
