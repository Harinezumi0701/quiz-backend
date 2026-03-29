# app/api/v1/role.py
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies.permissions import require_namespace_permission
from app.constants.permissions import PERMISSION_NAMESPACE_ROLES
from app.db.session import get_db
from app.models.users import User
from app.schemas.http_response import ErrorResponse
from app.schemas.role import RoleCreateRequest, RoleListResponse, RoleResponse, RoleUpdateRequest
from app.services import role_service
from app.utils.search_pagination import get_pagination_meta

router = APIRouter()


@router.get(
    "",
    response_model=RoleListResponse,
    summary="Get all roles",
    description="Get list of all roles with optional name search and pagination. Supports standard query parameters for filtering (key=value). For comma-separated values, use OR condition.",
    responses={
        200: {
            "description": "List of roles",
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def get_all_roles(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ROLES, "GET")
    ),
):
    """
    Get all roles with optional filtering and pagination.

    **Filter Options:**
    - **Format**: Use `key=value` query parameters (e.g., `?name=admin`)
    - **OR condition**: Use comma-separated values (e.g., `?name=admin,user`)
    
    **Search Keys:**
    - `name`: Search in role name (text search)
    
    **Examples:**
    - Simple filter: `?name=admin`
    - Multiple filters: `?name=admin&description=test` (if description search is supported)
    - OR condition: `?name=admin,user,guest`

    Requires permission: roles::read
    """
    request_params = dict(request.query_params)
    roles, total = role_service.get_all_roles_with_search(
        db, page=page, page_size=page_size, request_params=request_params
    )

    meta = get_pagination_meta(total, page, page_size)

    return RoleListResponse(data=roles, meta=meta)


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Get role by ID",
    description="Get a specific role by ID with permissions",
    responses={
        200: {
            "description": "Role details",
        },
        404: {
            "description": "Role not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def get_role_by_id(
    role_id: UUID = Path(
        ..., description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ROLES, "GET")
    ),
):
    """
    Get a specific role by ID with all permissions.

    - **role_id**: UUID of the role

    Requires permission: roles::read
    """
    role = role_service.get_role_by_id(db, role_id)

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found",
        )

    # Get permissions for the role
    from app.repository import role_repo

    permissions = role_repo.get_role_permissions(db, role_id)
    role_data = {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "default": role.default,
        "permissions": [
            {
                "id": perm.id,
                "permission": perm.permission,
                "name": perm.name,
                "description": perm.description,
                "created_at": perm.created_at,
            }
            for perm in permissions
        ],
        "created_at": role.created_at,
        "updated_at": role.updated_at,
    }

    return RoleResponse(data=role_data, meta={})


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
    description="Create a new role (requires permission)",
    responses={
        201: {
            "description": "Role created",
        },
        400: {
            "description": "Invalid input",
            "model": ErrorResponse,
        },
        409: {
            "description": "Role name already exists",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def create_role(
    role_data: RoleCreateRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ROLES, "POST")
    ),
):
    """
    Create a new role.

    - **name**: Role name (required, 1-100 characters, must be unique)
    - **description**: Role description (optional, max 500 characters)

    Requires permission: roles::create
    """
    role = role_service.create_role(db, role_data.name, role_data.description)

    # Get permissions for the role
    from app.repository import role_repo

    permissions = role_repo.get_role_permissions(db, role.id)
    role_response_data = {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "default": role.default,
        "permissions": [
            {
                "id": perm.id,
                "permission": perm.permission,
                "name": perm.name,
                "description": perm.description,
                "created_at": perm.created_at,
            }
            for perm in permissions
        ],
        "created_at": role.created_at,
        "updated_at": role.updated_at,
    }

    return RoleResponse(data=role_response_data, meta={})


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update a role",
    description="Update a role by ID (requires permission)",
    responses={
        200: {
            "description": "Role updated",
        },
        404: {
            "description": "Role not found",
            "model": ErrorResponse,
        },
        409: {
            "description": "Role name already exists",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def update_role(
    role_id: UUID = Path(
        ..., description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    role_data: RoleUpdateRequest = Body(...),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ROLES, "PUT")
    ),
):
    """
    Update a role by ID.

    - **role_id**: UUID of the role
    - **name**: New role name (optional, 1-100 characters, must be unique)
    - **description**: New role description (optional, max 500 characters)

    Requires permission: roles::update
    """
    update_dict = role_data.model_dump(exclude_unset=True)
    role = role_service.update_role(
        db, role_id, update_dict.get("name"), update_dict.get("description")
    )

    # Get permissions for the role
    from app.repository import role_repo

    permissions = role_repo.get_role_permissions(db, role.id)
    role_response_data = {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "default": role.default,
        "permissions": [
            {
                "id": perm.id,
                "permission": perm.permission,
                "name": perm.name,
                "description": perm.description,
                "created_at": perm.created_at,
            }
            for perm in permissions
        ],
        "created_at": role.created_at,
        "updated_at": role.updated_at,
    }

    return RoleResponse(data=role_response_data, meta={})


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a role",
    description="Delete a role by ID (soft delete, requires permission)",
    responses={
        200: {
            "description": "Role deleted successfully",
        },
        404: {
            "description": "Role not found",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
    },
)
def delete_role(
    role_id: UUID = Path(
        ..., description="Role ID", example="550e8400-e29b-41d4-a716-446655440000"
    ),
    db: Session = Depends(get_db),
    user: User = Depends(
        require_namespace_permission(PERMISSION_NAMESPACE_ROLES, "DELETE")
    ),
):
    """
    Delete a role by ID (soft delete).

    - **role_id**: UUID of the role

    Requires permission: roles::delete
    """
    role_service.delete_role(db, role_id)
    return {"message": "Role deleted successfully"}
