"""add_name_and_description_to_role_permissions

Revision ID: s9t0u1v2w3
Revises: ae0d19e5f99e
Create Date: 2025-01-17 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 's9t0u1v2w3'
down_revision: Union[str, Sequence[str], None] = 'ae0d19e5f99e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add name and description columns to role_permissions table."""
    op.add_column('role_permissions', sa.Column('name', sa.String(length=200), nullable=True))
    op.add_column('role_permissions', sa.Column('description', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Remove name and description columns from role_permissions table."""
    op.drop_column('role_permissions', 'description')
    op.drop_column('role_permissions', 'name')
