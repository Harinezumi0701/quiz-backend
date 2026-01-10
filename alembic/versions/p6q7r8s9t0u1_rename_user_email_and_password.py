"""rename_user_email_and_password

Revision ID: p6q7r8s9t0u1
Revises: o5p6q7r8s9t0
Create Date: 2025-01-17 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'p6q7r8s9t0u1'
down_revision: Union[str, Sequence[str], None] = 'o5p6q7r8s9t0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename user_email to email and user_password to password."""
    op.alter_column('users', 'user_email', new_column_name='email')
    op.alter_column('users', 'user_password', new_column_name='password')


def downgrade() -> None:
    """Revert changes: rename email back to user_email and password back to user_password."""
    op.alter_column('users', 'email', new_column_name='user_email')
    op.alter_column('users', 'password', new_column_name='user_password')
