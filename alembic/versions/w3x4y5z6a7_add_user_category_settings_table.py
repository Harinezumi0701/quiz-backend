"""add_user_category_settings_table

Revision ID: w3x4y5z6a7
Revises: v2w3x4y5z6
Create Date: 2026-04-19 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'w3x4y5z6a7'
down_revision: Union[str, Sequence[str], None] = 'v2w3x4y5z6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_category_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('uuidv7()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('categories.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('questions_per_day', sa.Integer(), nullable=False,
                  server_default=sa.text('20')),
        sa.Column('time_limit', sa.Integer(), nullable=False,
                  server_default=sa.text('60')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.UniqueConstraint('user_id', 'category_id', name='uq_user_category_settings'),
    )
    op.create_index('ix_user_category_settings_id', 'user_category_settings', ['id'], unique=False)
    op.create_index('ix_user_category_settings_user_id', 'user_category_settings', ['user_id'], unique=False)
    op.create_index('ix_user_category_settings_category_id', 'user_category_settings', ['category_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_user_category_settings_category_id', table_name='user_category_settings')
    op.drop_index('ix_user_category_settings_user_id', table_name='user_category_settings')
    op.drop_index('ix_user_category_settings_id', table_name='user_category_settings')
    op.drop_table('user_category_settings')
