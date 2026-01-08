"""add_is_multiple_choice_to_questions

Revision ID: h7i8j9k0l1m2
Revises: 5ff731ff1f1
Create Date: 2025-01-15 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'h7i8j9k0l1m2'
down_revision: Union[str, Sequence[str], None] = '5ff731ff1f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_multiple_choice column to questions table."""
    # Add is_multiple_choice column
    op.add_column(
        'questions',
        sa.Column('is_multiple_choice', sa.Boolean(), nullable=False, server_default='false')
    )
    
    # Update existing records: set is_multiple_choice = true if question has more than 1 correct answer
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE questions q
        SET is_multiple_choice = true
        WHERE (
            SELECT COUNT(*)
            FROM answers a
            WHERE a.question_id = q.id
            AND a.is_correct = true
            AND a.deleted_at IS NULL
        ) > 1
        AND q.deleted_at IS NULL
    """))


def downgrade() -> None:
    """Remove is_multiple_choice column from questions table."""
    op.drop_column('questions', 'is_multiple_choice')
