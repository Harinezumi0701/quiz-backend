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
    # Add description column (nullable, TEXT type)
    op.add_column(
        "tests",
        sa.Column("description", sa.Text(), nullable=True),
    )

    # Add time_limit column (nullable, INTEGER type - in seconds)
    op.add_column(
        "tests",
        sa.Column("time_limit", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Remove description and time_limit columns from tests table."""
    op.drop_column("tests", "time_limit")
    op.drop_column("tests", "description")
