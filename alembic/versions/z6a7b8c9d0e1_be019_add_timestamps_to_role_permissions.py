"""be019_add_timestamps_to_role_permissions

Revision ID: z6a7b8c9d0e1
Revises: y5z6a7b8c9d0
Create Date: 2026-03-29 00:00:00.000000

Aligns role_permissions with the soft-delete convention used by every other
table: adds updated_at and deleted_at columns.  No logic changes.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'z6a7b8c9d0e1'
down_revision: Union[str, Sequence[str], None] = 'y5z6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'role_permissions',
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    )
    op.add_column(
        'role_permissions',
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    )
    # Back-fill updated_at from created_at for existing rows
    op.execute("UPDATE role_permissions SET updated_at = created_at")


def downgrade() -> None:
    op.drop_column('role_permissions', 'deleted_at')
    op.drop_column('role_permissions', 'updated_at')
