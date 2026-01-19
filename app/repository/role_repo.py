# app/repository/role_repo.py
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, Tuple, Dict, Any
from app.models.roles import Role, RolePermission
from app.utils.search_pagination import paginate_query_with_multiple_filters


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
    page: int = 1,
    page_size: int = 10,
    request_params: Optional[Dict[str, Any]] = None,
) -> Tuple[list, int]:
    """
    Get all roles with optional filtering and pagination.
    
    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        request_params: Optional dict of request parameters for multiple filters
    
    Returns:
        Tuple[list, int]: List of roles and total count
    """
    query = db.query(Role).filter(Role.deleted_at.is_(None)).order_by(Role.created_at.desc())
    
    # Define search configuration
    search_config = {
        "name": {
            "column": Role.name,
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
    roles = paginated_query.all()
    
    # Load permissions for each role
    result = []
    for role in roles:
        permissions = get_role_permissions(db, role.id)
        result.append({
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'default': role.default,
            'permissions': [
                {
                    'id': perm.id,
                    'permission': perm.permission,
                    'name': perm.name,
                    'description': perm.description,
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


def update_role(db: Session, role_id: UUID, name: str = None, description: str = None) -> Role:
    """Update a role."""
    role = get_role_by_id(db, role_id)
    if not role:
        return None
    
    if name is not None:
        role.name = name
    if description is not None:
        role.description = description
    
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: UUID) -> bool:
    """Soft delete a role."""
    from datetime import datetime, timezone
    
    role = get_role_by_id(db, role_id)
    if not role:
        return False
    
    role.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True


def get_default_role(db: Session) -> Optional[Role]:
    """Get the default role for new users."""
    return db.query(Role).filter(
        Role.default == True,
        Role.deleted_at.is_(None)
    ).first()
