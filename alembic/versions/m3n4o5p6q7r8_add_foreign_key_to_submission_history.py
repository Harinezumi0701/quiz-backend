"""add_foreign_key_to_submission_history

Revision ID: m3n4o5p6q7r8
Revises: l2m3n4o5p6q7
Create Date: 2025-01-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'm3n4o5p6q7r8'
down_revision: Union[str, Sequence[str], None] = 'l2m3n4o5p6q7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add foreign key for user_id to submission_history table."""
    connection = op.get_bind()
    
    # Check and add foreign key for user_id in submission_history
    result = connection.execute(sa.text("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'submission_history' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%user_id%'
    """))
    if not result.fetchone():
        op.create_foreign_key(
            'fk_submission_history_user_id',
            'submission_history', 'users',
            ['user_id'], ['id']
        )


def downgrade() -> None:
    """Drop foreign key from submission_history table."""
    connection = op.get_bind()
    
    # Drop foreign key for submission_history table
    op.execute(sa.text("""
        DO $$ 
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'submission_history' 
                AND constraint_type = 'FOREIGN KEY'
                AND constraint_name = 'fk_submission_history_user_id'
            ) LOOP
                EXECUTE 'ALTER TABLE submission_history DROP CONSTRAINT ' || r.constraint_name;
            END LOOP;
        END $$;
    """))
