"""be020_add_activation_fields_to_users

Revision ID: d4e5f6a7b8c0
Revises: c3d4e5f6a7b9
Create Date: 2026-03-29 00:04:00.000000

Adds email activation fields to the users table.
Existing users are set to is_active=TRUE so they keep access.
New registrations will start with is_active=FALSE until email is confirmed.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e5f6a7b8c0'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns — default TRUE so existing rows are immediately active
    op.add_column(
        'users',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
    )
    op.add_column(
        'users',
        sa.Column('activation_token', sa.String(255), nullable=True),
    )
    op.add_column(
        'users',
        sa.Column('activation_expires_at', sa.TIMESTAMP(), nullable=True),
    )
    op.create_index('ix_users_activation_token', 'users', ['activation_token'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_activation_token', table_name='users')
    op.drop_column('users', 'activation_expires_at')
    op.drop_column('users', 'activation_token')
    op.drop_column('users', 'is_active')
