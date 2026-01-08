"""add_foreign_keys_to_submissions_and_history

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6
Create Date: 2025-01-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'l2m3n4o5p6q7'
down_revision: Union[str, Sequence[str], None] = 'k1l2m3n4o5p6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add foreign keys to submissions table."""
    connection = op.get_bind()
    
    # Add foreign keys for submissions table if they don't exist
    # Check and add foreign key for user_id
    result = connection.execute(sa.text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'submissions' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%user_id%'
    """))
    if not result.fetchone():
        op.create_foreign_key(
            'fk_submissions_user_id',
            'submissions', 'users',
            ['user_id'], ['id']
        )
    
    # Check and add foreign key for question_id
    result = connection.execute(sa.text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'submissions' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%question_id%'
    """))
    if not result.fetchone():
        op.create_foreign_key(
            'fk_submissions_question_id',
            'submissions', 'questions',
            ['question_id'], ['id']
        )
    
    # Check and add foreign key for answer_id
    result = connection.execute(sa.text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'submissions' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%answer_id%'
    """))
    if not result.fetchone():
        op.create_foreign_key(
            'fk_submissions_answer_id',
            'submissions', 'answers',
            ['answer_id'], ['id']
        )
    
    # Check and add foreign key for submission_history_id
    result = connection.execute(sa.text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'submissions' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%submission_history_id%'
    """))
    if not result.fetchone():
        op.create_foreign_key(
            'fk_submissions_submission_history_id',
            'submissions', 'submission_history',
            ['submission_history_id'], ['id']
        )


def downgrade() -> None:
    """Drop foreign keys from submissions table."""
    connection = op.get_bind()
    
    # Drop foreign keys for submissions table
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
                AND constraint_name IN (
                    'fk_submissions_user_id',
                    'fk_submissions_question_id',
                    'fk_submissions_answer_id',
                    'fk_submissions_submission_history_id'
                )
            ) LOOP
                EXECUTE 'ALTER TABLE submissions DROP CONSTRAINT ' || r.constraint_name;
            END LOOP;
        END $$;
    """))
