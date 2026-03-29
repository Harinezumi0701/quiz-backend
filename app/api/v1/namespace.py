# app/api/v1/namespace.py

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
from app.constants.permissions import PERMISSION_NAMESPACE_NAMESPACES
from app.db.session import get_db
from app.models.users import User
from app.schemas.http_response import ErrorResponse
from app.schemas.namespace import (
    NamespaceCreateRequest,
    NamespaceListResponse,
    NamespaceResponse,
    NamespaceUpdateRequest,
)
from app.services import namespace_service
from app.utils.search_pagination import get_pagination_meta

router = APIRouter()


@router.get(
    "",
    response_model=NamespaceListResponse,
    summary="Get all namespaces",
    description="Get list of all namespaces with optional name search and pagination. Supports standard query parameters for filtering (key=value). For comma-separated values, use OR condition.",
    responses={
        200: {
            "description": "List of namespaces",
        }
    },
)
def get_all_namespaces(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
):
    """
    Get all namespaces with optional name search and pagination.

    **Filter Options:**
    - **Format**: Use `key=value` query parameters (e.g., `?name=categories`)
    - **OR condition**: Use comma-separated values (e.g., `?name=ns1,ns2`)

    **Search Keys:**
    - `name`: Search in namespace name (text search)

    **Examples:**
    - Simple filter: `?name=categories`
    - Multiple filters: `?name=categories&prefix=cat`
    - OR condition: `?name=categories,users,roles`

    This endpoint is public and does not require authentication.
    """
    request_params = dict(request.query_params)
    namespaces, total = namespace_service.get_all_namespaces_with_search(
        db,
        page=page,
        page_size=page_size,
        request_params=request_params,
    )

    meta = get_pagination_meta(total, page, page_size)

    return NamespaceListResponse(data=namespaces, meta=meta)


@router.get(
    "/{namespace_id}",
    response_model=NamespaceResponse,
    summary="Get namespace by ID",
    description="Get a specific namespace by ID",
    responses={
        200: {
            "description": "Namespace details",
        },
        404: {
            "description": "Namespace not found",
            "model": ErrorResponse,
        },
    },
)
def get_namespace_by_id(
    namespace_id: str = Path(
        ..., description="Namespace ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    db: Session = Depends(get_db),
):
    """
    Get a specific namespace by ID.

    - **namespace_id**: UUID of the namespace

    This endpoint is public and does not require authentication.
    """
    namespace = namespace_service.get_namespace_by_id(db, namespace_id)

    if not namespace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Namespace with ID {namespace_id} not found",
        )

    return NamespaceResponse(data=namespace, meta={})


@router.post(
    "",
    response_model=NamespaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new namespace",
    description="Create a new namespace (requires permission)",
    responses={
        201: {
            "description": "Namespace created",
        },
        400: {
            "description": "Namespace name or prefix already exists",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def create_namespace(
    namespace_data: NamespaceCreateRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_NAMESPACES, "POST")
    ),
):
    """
    Create a new namespace.

    - **name**: Namespace name (1-100 characters)
    - **prefix**: Namespace prefix (1-100 characters)
    - **description**: Namespace description (optional, max 500 characters)

    Requires permission: namespaces::create
    """
    from app.models.namespaces import Namespace

    # Check if namespace name already exists
    existing_namespace = (
        db.query(Namespace)
        .filter(Namespace.name == namespace_data.name, Namespace.deleted_at.is_(None))
        .first()
    )
    if existing_namespace:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Namespace with name '{namespace_data.name}' already exists",
        )

    # Check if namespace prefix already exists
    existing_prefix = (
        db.query(Namespace)
        .filter(
            Namespace.prefix == namespace_data.prefix, Namespace.deleted_at.is_(None)
        )
        .first()
    )
    if existing_prefix:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Namespace with prefix '{namespace_data.prefix}' already exists",
        )

    namespace = namespace_service.create_namespace(
        db, namespace_data.name, namespace_data.prefix, namespace_data.description
    )
    return NamespaceResponse(data=namespace, meta={})


@router.put(
    "/{namespace_id}",
    response_model=NamespaceResponse,
    summary="Update a namespace",
    description="Update a namespace by ID (requires permission)",
    responses={
        200: {
            "description": "Namespace updated",
        },
        404: {
            "description": "Namespace not found",
            "model": ErrorResponse,
        },
        400: {
            "description": "Namespace name or prefix already exists",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def update_namespace(
    namespace_id: str = Path(
        ..., description="Namespace ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    namespace_data: NamespaceUpdateRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_NAMESPACES, "PUT")
    ),
):
    """
    Update a namespace by ID.

    - **namespace_id**: UUID of the namespace
    - **name**: New namespace name (optional, 1-100 characters)
    - **prefix**: New namespace prefix (optional, 1-100 characters)
    - **description**: New namespace description (optional, max 500 characters)

    Requires permission: namespaces::update
    """
    from app.models.namespaces import Namespace

    # Check if namespace exists
    existing_namespace = namespace_service.get_namespace_by_id(db, namespace_id)
    if not existing_namespace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Namespace with ID {namespace_id} not found",
        )

    # Check if new name already exists (excluding current namespace)
    if namespace_data.name:
        existing_name = (
            db.query(Namespace)
            .filter(
                Namespace.name == namespace_data.name,
                Namespace.id != namespace_id,
                Namespace.deleted_at.is_(None),
            )
            .first()
        )
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Namespace with name '{namespace_data.name}' already exists",
            )

    # Check if new prefix already exists (excluding current namespace)
    if namespace_data.prefix:
        existing_prefix = (
            db.query(Namespace)
            .filter(
                Namespace.prefix == namespace_data.prefix,
                Namespace.id != namespace_id,
                Namespace.deleted_at.is_(None),
            )
            .first()
        )
        if existing_prefix:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Namespace with prefix '{namespace_data.prefix}' already exists",
            )

    namespace = namespace_service.update_namespace(
        db,
        namespace_id,
        namespace_data.name,
        namespace_data.prefix,
        namespace_data.description,
    )
    return NamespaceResponse(data=namespace, meta={})


@router.delete(
    "/{namespace_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a namespace",
    description="Delete a namespace by ID (soft delete, requires permission)",
    responses={
        200: {
            "description": "Namespace deleted successfully",
        },
        404: {
            "description": "Namespace not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def delete_namespace(
    namespace_id: str = Path(
        ..., description="Namespace ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_NAMESPACES, "DELETE")
    ),
):
    """
    Delete a namespace by ID (soft delete).

    - **namespace_id**: UUID of the namespace

    Requires permission: namespaces::delete
    """
    deleted = namespace_service.delete_namespace(db, namespace_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Namespace with ID {namespace_id} not found",
        )

    return {"message": "Namespace deleted successfully"}
