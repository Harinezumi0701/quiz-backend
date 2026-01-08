"""remove_deleted_at_from_refresh_tokens

Revision ID: 8e64cf816f4f
Revises: g1h2i3j4k5l6
Create Date: 2025-01-15 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8e64cf816f4f'
down_revision: Union[str, Sequence[str], None] = 'g1h2i3j4k5l6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove deleted_at column from refresh_tokens table."""
    op.drop_column('refresh_tokens', 'deleted_at')


def downgrade() -> None:
    """Add deleted_at column back to refresh_tokens table."""
    op.add_column('refresh_tokens', sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True))
