# app/repository/permission_repo.py
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, Tuple, Dict, Any
from app.models.roles import RolePermission, Role
from app.utils.search_pagination import paginate_query_with_multiple_filters
from app.utils.datetime_utils import datetime_to_timestamp


def get_permission_by_id(db: Session, permission_id: UUID) -> Optional[RolePermission]:
    """Get permission by ID."""
    return db.query(RolePermission).filter(RolePermission.id == permission_id).first()


def get_all_permissions(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all permissions with optional filtering and pagination.
    
    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for multiple filters
    
    Returns:
        Tuple[list, int]: List of permissions and total count
    """
    query = db.query(RolePermission).order_by(RolePermission.created_at.desc())
    
    # Define search configuration
    search_config = {
        "permission": {
            "column": RolePermission.permission,
            "type": "text",
            "case_sensitive": False,
        },
        "role_id": {
            "column": RolePermission.role_id,
            "type": "exact",
        },
        "name": {
            "column": RolePermission.name,
            "type": "text",
            "case_sensitive": False,
        },
    }
    
    # Apply search filter and pagination
    paginated_query, total = paginate_query_with_multiple_filters(
        query,
        request_params=request_params or {},
        search_config=search_config,
        page=page,
        page_size=page_size,
    )
    
    # Execute query
    permissions = paginated_query.all()
    
    # Format results
    result = []
    for perm in permissions:
        result.append({
            "id": perm.id,
            "role_id": perm.role_id,
            "permission": perm.permission,
            "name": perm.name,
            "description": perm.description,
            "created_at": datetime_to_timestamp(perm.created_at),
        })
    
    return result, total


def create_permission(
    db: Session, role_id: UUID, permission: str, name: str = None, description: str = None
) -> RolePermission:
    """Create a new permission."""
    # Verify role exists
    role = db.query(Role).filter(Role.id == role_id, Role.deleted_at.is_(None)).first()
    if not role:
        return None
    
    permission_obj = RolePermission(
        role_id=role_id, permission=permission, name=name, description=description
    )
    db.add(permission_obj)
    db.commit()
    db.refresh(permission_obj)
    return permission_obj


def update_permission(
    db: Session,
    permission_id: UUID,
    role_id: UUID = None,
    permission: str = None,
    name: str = None,
    description: str = None,
) -> Optional[RolePermission]:
    """Update a permission."""
    permission_obj = get_permission_by_id(db, permission_id)
    if not permission_obj:
        return None
    
    # Verify role exists if role_id is being updated
    if role_id is not None:
        role = db.query(Role).filter(Role.id == role_id, Role.deleted_at.is_(None)).first()
        if not role:
            return None
        permission_obj.role_id = role_id
    
    if permission is not None:
        permission_obj.permission = permission
    
    if name is not None:
        permission_obj.name = name
    
    if description is not None:
        permission_obj.description = description
    
    db.commit()
    db.refresh(permission_obj)
    return permission_obj


def delete_permission(db: Session, permission_id: UUID) -> bool:
    """Delete a permission."""
    permission_obj = get_permission_by_id(db, permission_id)
    if not permission_obj:
        return False
    
    db.delete(permission_obj)
    db.commit()
    return True
