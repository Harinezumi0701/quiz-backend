"""drop_category_column_from_questions

Revision ID: f0a1b2c3d4e5
Revises: e9f0a1b2c3d4
Create Date: 2025-01-08 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f0a1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = 'e9f0a1b2c3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop the old category column from questions table.
    
    This column was kept for backward compatibility during the transition
    from string-based categories to the categories table. Now that the
    migration is complete, we can safely remove it.
    """
    # Check if column exists before dropping (in case it was already dropped)
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'questions' 
                AND column_name = 'category'
            ) THEN
                ALTER TABLE questions DROP COLUMN category;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """Re-add the category column for rollback purposes."""
    # Add category column back (nullable, as it may not have all data)
    op.add_column('questions', sa.Column('category', sa.String(length=100), nullable=True))
    
    # Populate category column from categories table
    op.execute("""
        UPDATE questions q
        SET category = c.name
        FROM categories c
        WHERE q.category_id = c.id;
    """)
