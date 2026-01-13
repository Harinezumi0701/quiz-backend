"""create_namespaces_table

Revision ID: t0u1v2w3x4
Revises: s9t0u1v2w3
Create Date: 2025-01-17 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 't0u1v2w3x4'
down_revision: Union[str, Sequence[str], None] = 's9t0u1v2w3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create namespaces table."""
    op.create_table(
        'namespaces',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuidv7()')),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('prefix', sa.String(length=100), nullable=False, unique=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    )
    op.create_index(op.f('ix_namespaces_id'), 'namespaces', ['id'], unique=False)
    op.create_index(op.f('ix_namespaces_name'), 'namespaces', ['name'], unique=True)
    op.create_index(op.f('ix_namespaces_prefix'), 'namespaces', ['prefix'], unique=True)


def downgrade() -> None:
    """Drop namespaces table."""
    op.drop_index(op.f('ix_namespaces_prefix'), table_name='namespaces')
    op.drop_index(op.f('ix_namespaces_name'), table_name='namespaces')
    op.drop_index(op.f('ix_namespaces_id'), table_name='namespaces')
    op.drop_table('namespaces')
