"""remove_role_column_from_users

Revision ID: r8s9t0u1v2w3
Revises: q7r8s9t0u1v2
Create Date: 2025-01-17 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "r8s9t0u1v2w3"
down_revision: Union[str, Sequence[str], None] = "q7r8s9t0u1v2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove role column from users table."""
    # Check if role column exists before dropping
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col["name"] for col in inspector.get_columns("users")]

    if "role" in columns:
        op.drop_column("users", "role")


def downgrade() -> None:
    """Revert changes: add role column back."""
    # Check if role column exists before adding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col["name"] for col in inspector.get_columns("users")]

    if "role" not in columns:
        op.add_column(
            "users",
            sa.Column(
                "role", sa.String(length=50), nullable=False, server_default="user"
            ),
        )
