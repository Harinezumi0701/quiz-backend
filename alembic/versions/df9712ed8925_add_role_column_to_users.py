"""add role column to users

Revision ID: df9712ed8925
Revises: p6q7r8s9t0u1
Create Date: 2026-01-10 18:26:43.298286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df9712ed8925'
down_revision: Union[str, Sequence[str], None] = 'p6q7r8s9t0u1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if role column exists before adding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('users')]

    if 'role' not in columns:
        # Add role column with default value 'user'
        op.add_column('users', sa.Column('role', sa.String(length=50), nullable=False, server_default='user'))


def downgrade() -> None:
    """Downgrade schema."""
    # Check if role column exists before dropping
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('users')]

    if 'role' in columns:
        # Remove role column
        op.drop_column('users', 'role')
