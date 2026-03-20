"""create_user_category_access_table

Revision ID: x4y5z6a7b8c9
Revises: w3x4y5z6a7b8
Create Date: 2026-03-20 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'x4y5z6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'w3x4y5z6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_category_access',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuidv7()')),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'category_id', name='uq_user_category_access'),
    )
    op.create_index(op.f('ix_user_category_access_id'), 'user_category_access', ['id'], unique=False)
    op.create_index(op.f('ix_user_category_access_user_id'), 'user_category_access', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_category_access_category_id'), 'user_category_access', ['category_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_category_access_category_id'), table_name='user_category_access')
    op.drop_index(op.f('ix_user_category_access_user_id'), table_name='user_category_access')
    op.drop_index(op.f('ix_user_category_access_id'), table_name='user_category_access')
    op.drop_table('user_category_access')
