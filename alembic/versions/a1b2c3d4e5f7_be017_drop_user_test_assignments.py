"""be017_drop_user_test_assignments

Revision ID: a1b2c3d4e5f7
Revises: z6a7b8c9d0e1
Create Date: 2026-03-29 00:01:00.000000

Drops the user_test_assignments table (legacy feature removed).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, Sequence[str], None] = 'z6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('user_test_assignments')


def downgrade() -> None:
    op.create_table(
        'user_test_assignments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuidv7()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('test_id', UUID(as_uuid=True), sa.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('assigned_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.UniqueConstraint('user_id', 'test_id', name='uq_user_test_assignments_user_test'),
    )
