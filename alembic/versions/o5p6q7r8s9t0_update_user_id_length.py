"""update_user_id_length

Revision ID: o5p6q7r8s9t0
Revises: n4o5p6q7r8s9
Create Date: 2025-01-17 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'o5p6q7r8s9t0'
down_revision: Union[str, Sequence[str], None] = 'n4o5p6q7r8s9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Change user_id column length from 6 to 125 characters."""
    op.alter_column('users', 'user_id',
                    existing_type=sa.String(length=6),
                    type_=sa.String(length=125),
                    existing_nullable=False)


def downgrade() -> None:
    """Revert user_id column length back to 6 characters."""
    # Note: This may fail if any user_id values exceed 6 characters
    op.alter_column('users', 'user_id',
                    existing_type=sa.String(length=125),
                    type_=sa.String(length=6),
                    existing_nullable=False)
