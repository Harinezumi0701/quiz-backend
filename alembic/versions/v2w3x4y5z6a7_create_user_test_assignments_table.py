"""create_user_test_assignments_table

Revision ID: v2w3x4y5z6a7
Revises: v2w3x4y5z6
Create Date: 2025-02-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'v2w3x4y5z6a7'
down_revision: Union[str, Sequence[str], None] = 'v2w3x4y5z6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_test_assignments table."""
    op.create_table(
        'user_test_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuidv7()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('test_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'test_id', name='uq_user_test_assignment'),
    )
    op.create_index(op.f('ix_user_test_assignments_id'), 'user_test_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_user_test_assignments_test_id'), 'user_test_assignments', ['test_id'], unique=False)
    op.create_index(op.f('ix_user_test_assignments_user_id'), 'user_test_assignments', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop user_test_assignments table."""
    op.drop_index(op.f('ix_user_test_assignments_user_id'), table_name='user_test_assignments')
    op.drop_index(op.f('ix_user_test_assignments_test_id'), table_name='user_test_assignments')
    op.drop_index(op.f('ix_user_test_assignments_id'), table_name='user_test_assignments')
    op.drop_table('user_test_assignments')
