# app/api/v1/permission.py
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies.permissions import require_namespace_permission
from app.constants.permissions import PERMISSION_NAMESPACE_ROLES
from app.db.session import get_db
from app.models.users import User
from app.schemas.http_response import ErrorResponse
from app.schemas.permission import (
    PermissionCreateRequest,
    PermissionListResponse,
    PermissionResponse,
    PermissionUpdateRequest,
)
from app.services import permission_service
from app.utils.search_pagination import get_pagination_meta

router = APIRouter()


@router.get(
    "",
    response_model=PermissionListResponse,
    summary="Get all permissions",
    description="Get list of all permissions with optional search and pagination. Supports standard query parameters for filtering (key=value). For comma-separated values, use OR condition.",
    responses={
        200: {
            "description": "List of permissions",
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def get_all_permissions(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ROLES, "GET")
    ),
):
    """
    Get all permissions with optional filtering and pagination.

    **Filter Options:**
    - **Format**: Use `key=value` query parameters (e.g., `?permission=categories`)
    - **OR condition**: Use comma-separated values (e.g., `?role_id=id1,id2`)
    
    **Search Keys:**
    - `permission`: Search in permission string (text search)
    - `role_id`: Filter by role ID (exact match)
    - `name`: Search in permission name (text search)
    
    **Examples:**
    - Simple filter: `?permission=categories`
    - Multiple filters: `?permission=categories&role_id=550e8400-e29b-41d4-a716-446655440000`
    - Search by name: `?name=Read Categories`
    - OR condition: `?role_id=id1,id2,id3`

    Requires permission: roles::read
    """
    request_params = dict(request.query_params)
    permissions, total = permission_service.get_all_permissions(
        db,
        page=page,
        page_size=page_size,
        request_params=request_params,
    )

    meta = get_pagination_meta(total, page, page_size)

    return PermissionListResponse(data=permissions, meta=meta)


@router.get(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Get permission by ID",
    description="Get a specific permission by ID",
    responses={
        200: {
            "description": "Permission details",
        },
        404: {
            "description": "Permission not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def get_permission_by_id(
    permission_id: UUID = Path(
        ..., description="Permission ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ROLES, "GET")
    ),
):
    """
    Get a specific permission by ID.

    - **permission_id**: UUID of the permission

    Requires permission: roles::read
    """
    from app.utils.datetime_utils import datetime_to_timestamp

    permission = permission_service.get_permission_by_id(db, permission_id)

    permission_data = {
        "id": permission.id,
        "role_id": permission.role_id,
        "permission": permission.permission,
        "name": permission.name,
        "description": permission.description,
        "created_at": datetime_to_timestamp(permission.created_at),
    }

    return PermissionResponse(data=permission_data, meta={})


@router.post(
    "",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new permission",
    description="Create a new permission (requires permission)",
    responses={
        201: {
            "description": "Permission created",
        },
        400: {
            "description": "Invalid input",
            "model": ErrorResponse,
        },
        404: {
            "description": "Role not found",
            "model": ErrorResponse,
        },
        409: {
            "description": "Permission already exists for this role",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def create_permission(
    permission_data: PermissionCreateRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ROLES, "POST")
    ),
):
    """
    Create a new permission.

    - **role_id**: Role ID (required)
    - **permission**: Permission string (required, format: namespace::action or *::*)
    - **name**: Permission name (optional)
    - **description**: Permission description (optional)

    Requires permission: roles::create
    """
    from app.utils.datetime_utils import datetime_to_timestamp

    permission = permission_service.create_permission(
        db,
        permission_data.role_id,
        permission_data.permission,
        permission_data.name,
        permission_data.description,
    )

    permission_response_data = {
        "id": permission.id,
        "role_id": permission.role_id,
        "permission": permission.permission,
        "name": permission.name,
        "description": permission.description,
        "created_at": datetime_to_timestamp(permission.created_at),
    }

    return PermissionResponse(data=permission_response_data, meta={})


@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
    summary="Update a permission",
    description="Update a permission by ID (requires permission)",
    responses={
        200: {
            "description": "Permission updated",
        },
        404: {
            "description": "Permission or role not found",
            "model": ErrorResponse,
        },
        409: {
            "description": "Permission already exists for this role",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def update_permission(
    permission_id: UUID = Path(
        ..., description="Permission ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    permission_data: PermissionUpdateRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ROLES, "PUT")
    ),
):
    """
    Update a permission by ID.

    - **permission_id**: UUID of the permission
    - **role_id**: New role ID (optional)
    - **permission**: New permission string (optional, format: namespace::action or *::*)
    - **name**: New permission name (optional)
    - **description**: New permission description (optional)

    Requires permission: roles::update
    """
    from app.utils.datetime_utils import datetime_to_timestamp

    update_dict = permission_data.model_dump(exclude_unset=True)
    permission = permission_service.update_permission(
        db,
        permission_id,
        update_dict.get("role_id"),
        update_dict.get("permission"),
        update_dict.get("name"),
        update_dict.get("description"),
    )

    permission_response_data = {
        "id": permission.id,
        "role_id": permission.role_id,
        "permission": permission.permission,
        "name": permission.name,
        "description": permission.description,
        "created_at": datetime_to_timestamp(permission.created_at),
    }

    return PermissionResponse(data=permission_response_data, meta={})


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a permission",
    description="Delete a permission by ID (requires permission)",
    responses={
        200: {
            "description": "Permission deleted successfully",
        },
        404: {
            "description": "Permission not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def delete_permission(
    permission_id: UUID = Path(
        ..., description="Permission ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ROLES, "DELETE")
    ),
):
    """
    Delete a permission by ID.

    - **permission_id**: UUID of the permission

    Requires permission: roles::delete
    """
    permission_service.delete_permission(db, permission_id)
    return {"message": "Permission deleted successfully"}
