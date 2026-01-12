"""add_rbac_tables_and_admin_role

Revision ID: q7r8s9t0u1v2
Revises: df9712ed8925
Create Date: 2025-01-17 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'q7r8s9t0u1v2'
down_revision: Union[str, Sequence[str], None] = 'df9712ed8925'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create RBAC tables and add admin role with *::* permission."""
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuidv7()')),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)

    # Create role_permissions table
    op.create_table(
        'role_permissions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuidv7()')),
        sa.Column('role_id', UUID(as_uuid=True), nullable=False),
        sa.Column('permission', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_role_permissions_id'), 'role_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_role_permissions_role_id'), 'role_permissions', ['role_id'], unique=False)
    op.create_index(op.f('ix_role_permissions_permission'), 'role_permissions', ['permission'], unique=False)

    # Add role_id column to users table
    op.add_column('users', sa.Column('role_id', UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_users_role_id', 'users', 'roles', ['role_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_users_role_id'), 'users', ['role_id'], unique=False)

    # Create admin role with *::* permission
    connection = op.get_bind()
    # Insert admin role and get the ID
    result = connection.execute(
        sa.text("""
            INSERT INTO roles (id, name, description, created_at, updated_at)
            VALUES (uuidv7(), 'admin', 'Administrator with full permissions', NOW(), NOW())
            RETURNING id
        """)
    )
    admin_role_id = result.scalar()

    # Insert *::* permission for admin role
    connection.execute(
        sa.text("""
            INSERT INTO role_permissions (id, role_id, permission, created_at)
            VALUES (uuidv7(), :role_id, '*::*', NOW())
        """),
        {'role_id': admin_role_id}
    )


def downgrade() -> None:
    """Revert RBAC changes."""
    # Drop foreign key and index from users table
    op.drop_constraint('fk_users_role_id', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_role_id'), table_name='users')
    op.drop_column('users', 'role_id')

    # Drop role_permissions table
    op.drop_index(op.f('ix_role_permissions_permission'), table_name='role_permissions')
    op.drop_index(op.f('ix_role_permissions_role_id'), table_name='role_permissions')
    op.drop_index(op.f('ix_role_permissions_id'), table_name='role_permissions')
    op.drop_table('role_permissions')

    # Drop roles table
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
