"""add_default_column_to_roles

Revision ID: v2w3x4y5z6
Revises: u1v2w3x4y5
Create Date: 2025-01-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'v2w3x4y5z6'
down_revision: Union[str, Sequence[str], None] = 'u1v2w3x4y5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add default column to roles table."""
    op.add_column('roles', sa.Column('default', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)


def downgrade() -> None:
    """Remove default column from roles table."""
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_column('roles', 'default')
