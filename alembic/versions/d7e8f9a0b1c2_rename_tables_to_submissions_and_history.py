"""rename_tables_to_submissions_and_history

Revision ID: d7e8f9a0b1c2
Revises: c8d9e1f2a3b4
Create Date: 2024-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd7e8f9a0b1c2'
down_revision: Union[str, Sequence[str], None] = 'c8d9e1f2a3b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename tables and columns to match new model structure."""
    # Step 1: Drop trigger on submissions table (will recreate for submission_history)
    op.execute("DROP TRIGGER IF EXISTS update_submissions_updated_at ON submissions;")
    
    # Step 2: Rename submissions table (submission history) to submission_history
    op.rename_table('submissions', 'submission_history')
    
    # Step 3: Rename column answer_count to submission_count in submission_history
    op.alter_column('submission_history', 'answer_count',
                    new_column_name='submission_count',
                    existing_type=sa.Integer(),
                    existing_nullable=False)
    
    # Step 4: Recreate trigger for submission_history table
    op.execute("""
        CREATE TRIGGER update_submission_history_updated_at 
        BEFORE UPDATE ON submission_history 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    # Step 5: Update index name for submission_history
    op.drop_index(op.f('ix_submissions_id'), table_name='submission_history')
    op.create_index(op.f('ix_submission_history_id'), 'submission_history', ['id'], unique=False)
    
    # Step 6: Rename responses table to submissions
    op.rename_table('responses', 'submissions')
    
    # Step 7: Rename column submission_id to submission_history_id in submissions table
    op.alter_column('submissions', 'submission_id',
                    new_column_name='submission_history_id',
                    existing_type=sa.Integer(),
                    existing_nullable=True)
    
    # Step 8: Drop old foreign key and create new one with correct name
    op.drop_constraint('fk_responses_submission_id', 'submissions', type_='foreignkey')
    op.create_foreign_key('fk_submissions_submission_history_id', 
                         'submissions', 'submission_history', 
                         ['submission_history_id'], ['id'])


def downgrade() -> None:
    """Revert table and column renames."""
    # Step 1: Revert foreign key
    op.drop_constraint('fk_submissions_submission_history_id', 'submissions', type_='foreignkey')
    op.create_foreign_key('fk_responses_submission_id', 
                         'submissions', 'submission_history', 
                         ['submission_history_id'], ['id'])
    
    # Step 2: Revert column name in submissions table
    op.alter_column('submissions', 'submission_history_id',
                    new_column_name='submission_id',
                    existing_type=sa.Integer(),
                    existing_nullable=True)
    
    # Step 3: Revert table name from submissions to responses
    op.rename_table('submissions', 'responses')
    
    # Step 4: Drop trigger on submission_history and recreate for submissions
    op.execute("DROP TRIGGER IF EXISTS update_submission_history_updated_at ON submission_history;")
    
    # Step 5: Revert index name
    op.drop_index(op.f('ix_submission_history_id'), table_name='submission_history')
    op.create_index(op.f('ix_submissions_id'), 'submission_history', ['id'], unique=False)
    
    # Step 6: Revert column name in submission_history table
    op.alter_column('submission_history', 'submission_count',
                    new_column_name='answer_count',
                    existing_type=sa.Integer(),
                    existing_nullable=False)
    
    # Step 7: Revert table name from submission_history to submissions
    op.rename_table('submission_history', 'submissions')
    
    # Step 8: Recreate trigger for submissions table
    op.execute("""
        CREATE TRIGGER update_submissions_updated_at 
        BEFORE UPDATE ON submissions 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """)

