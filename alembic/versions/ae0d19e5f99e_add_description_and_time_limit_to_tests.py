"""add_description_and_time_limit_to_tests

Revision ID: ae0d19e5f99e
Revises: r8s9t0u1v2w3
Create Date: 2025-01-20 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ae0d19e5f99e"
down_revision: Union[str, Sequence[str], None] = "r8s9t0u1v2w3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add description and time_limit columns to tests table."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col["name"] for col in inspector.get_columns("tests")]

    # Add description column (nullable, TEXT type) if not exists
    if "description" not in columns:
        op.add_column(
            "tests",
            sa.Column("description", sa.Text(), nullable=True),
        )

    # Add time_limit column if not exists
    if "time_limit" not in columns:
        # Add time_limit column (nullable first)
        op.add_column(
            "tests",
            sa.Column("time_limit", sa.Integer(), nullable=True),
        )

        # Set default value for existing records (60 minutes = 1 hour)
        connection.execute(
            sa.text("UPDATE tests SET time_limit = 60 WHERE time_limit IS NULL")
        )

        # Make time_limit not nullable
        op.alter_column(
            "tests",
            "time_limit",
            nullable=False,
            server_default="60",
        )
    else:
        # Column exists, but might be nullable - ensure it's not nullable
        # Check if column is nullable
        time_limit_col = next(
            (
                col
                for col in inspector.get_columns("tests")
                if col["name"] == "time_limit"
            ),
            None,
        )
        if time_limit_col and time_limit_col.get("nullable", True):
            # Set default value for NULL records (60 minutes = 1 hour)
            connection.execute(
                sa.text("UPDATE tests SET time_limit = 60 WHERE time_limit IS NULL")
            )
            # Make time_limit not nullable
            op.alter_column(
                "tests",
                "time_limit",
                nullable=False,
                server_default="60",
            )


def downgrade() -> None:
    """Remove description and time_limit columns from tests table."""
    op.drop_column("tests", "time_limit")
    op.drop_column("tests", "description")
