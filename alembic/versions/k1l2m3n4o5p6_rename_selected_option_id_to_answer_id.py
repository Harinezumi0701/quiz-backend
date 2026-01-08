"""rename_selected_option_id_to_answer_id

Revision ID: k1l2m3n4o5p6
Revises: i8j9k0l1m2n3
Create Date: 2025-01-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'k1l2m3n4o5p6'
down_revision: Union[str, Sequence[str], None] = 'i8j9k0l1m2n3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename selected_option_id column to answer_id in submissions table."""
    connection = op.get_bind()
    
    # Check if column exists and rename it
    result = connection.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'submissions' 
        AND column_name = 'selected_option_id'
    """))
    
    if result.fetchone():
        # Drop existing foreign key constraint if exists
        op.execute(sa.text("""
            DO $$ 
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN (
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = 'submissions' 
                    AND constraint_type = 'FOREIGN KEY'
                    AND constraint_name LIKE '%selected_option_id%'
                ) LOOP
                    EXECUTE 'ALTER TABLE submissions DROP CONSTRAINT ' || r.constraint_name;
                END LOOP;
            END $$;
        """))
        
        # Rename column
        op.alter_column('submissions', 'selected_option_id', new_column_name='answer_id')


def downgrade() -> None:
    """Revert column rename back to selected_option_id."""
    connection = op.get_bind()
    
    # Rename column back
    result = connection.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'submissions' 
        AND column_name = 'answer_id'
    """))
    
    if result.fetchone():
        op.alter_column('submissions', 'answer_id', new_column_name='selected_option_id')
