# app/repository/role_repo.py
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, Tuple, Dict, Any
from app.models.roles import Role, RolePermission
from app.utils.search_pagination import paginate_query, paginate_query_with_multiple_filters


def get_role_by_name(db: Session, name: str) -> Role:
    """Get role by name."""
    return db.query(Role).filter(Role.name == name, Role.deleted_at.is_(None)).first()


def get_role_by_id(db: Session, role_id: UUID) -> Role:
    """Get role by ID."""
    return db.query(Role).filter(Role.id == role_id, Role.deleted_at.is_(None)).first()


def get_all_roles(db: Session):
    """Get all active roles."""
    return db.query(Role).filter(Role.deleted_at.is_(None)).all()


def get_all_roles_with_search(
    db: Session,
    search_key: Optional[str] = None,
    search_value: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all roles with optional filtering and pagination.
    
    Args:
        db: Database session
        search_key: Search key (only "name" is supported)
        search_value: Value to search for in role name
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for multiple filters
    
    Returns:
        Tuple[list, int]: List of roles and total count
    """
    query = db.query(Role).filter(Role.deleted_at.is_(None))
    
    # Define search configuration
    search_config = {
        "name": {
            "column": Role.name,
            "type": "text",
            "case_sensitive": False,
        },
    }
    
    # Apply search filter and pagination
    if request_params:
        paginated_query, total = paginate_query_with_multiple_filters(
            query,
            request_params=request_params,
            search_config=search_config,
            page=page,
            page_size=page_size,
        )
    else:
        paginated_query, total = paginate_query(
            query,
            search_key=search_key,
            search_value=search_value,
            search_config=search_config,
            page=page,
            page_size=page_size,
        )
    
    # Execute query
    roles = paginated_query.all()
    
    # Load permissions for each role
    result = []
    for role in roles:
        permissions = get_role_permissions(db, role.id)
        result.append({
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'permissions': [
                {
                    'id': perm.id,
                    'permission': perm.permission,
                    'created_at': perm.created_at,
                }
                for perm in permissions
            ],
            'created_at': role.created_at,
            'updated_at': role.updated_at,
        })
    
    return result, total


def create_role(db: Session, name: str, description: str = None) -> Role:
    """Create a new role."""
    role = Role(name=name, description=description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def get_role_permissions(db: Session, role_id: UUID):
    """Get all permissions for a role."""
    return db.query(RolePermission).filter(RolePermission.role_id == role_id).all()


def add_role_permission(db: Session, role_id: UUID, permission: str) -> RolePermission:
    """Add a permission to a role."""
    role_permission = RolePermission(role_id=role_id, permission=permission)
    db.add(role_permission)
    db.commit()
    db.refresh(role_permission)
    return role_permission


def remove_role_permission(db: Session, role_id: UUID, permission: str):
    """Remove a permission from a role."""
    db.query(RolePermission).filter(
        RolePermission.role_id == role_id, RolePermission.permission == permission
    ).delete()
    db.commit()
