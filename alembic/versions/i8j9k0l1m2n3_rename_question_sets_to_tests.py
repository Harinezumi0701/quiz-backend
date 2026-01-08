"""rename_question_sets_to_tests

Revision ID: i8j9k0l1m2n3
Revises: h7i8j9k0l1m2
Create Date: 2025-01-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'i8j9k0l1m2n3'
down_revision: Union[str, Sequence[str], None] = 'h7i8j9k0l1m2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename question_sets table to tests and question_set_id column to test_id."""
    # Step 1: Drop foreign key constraint in questions table
    op.drop_constraint('questions_question_set_id_fkey', 'questions', type_='foreignkey')
    
    # Step 2: Drop index on question_set_id
    op.drop_index(op.f('ix_questions_question_set_id'), table_name='questions')
    
    # Step 3: Rename the column in questions table
    op.alter_column('questions', 'question_set_id', new_column_name='test_id')
    
    # Step 4: Rename the table
    op.rename_table('question_sets', 'tests')
    
    # Step 5: Rename indexes
    op.execute(sa.text("ALTER INDEX IF EXISTS ix_question_sets_id RENAME TO ix_tests_id"))
    op.execute(sa.text("ALTER INDEX IF EXISTS ix_question_sets_category_id RENAME TO ix_tests_category_id"))
    
    # Step 6: Rename foreign key constraint in tests table (if exists)
    connection = op.get_bind()
    try:
        connection.execute(sa.text("""
            ALTER TABLE tests 
            RENAME CONSTRAINT question_sets_category_id_fkey TO tests_category_id_fkey
        """))
    except:
        # Constraint might not exist or have different name, skip
        pass
    
    # Step 7: Create new index on test_id
    op.create_index(op.f('ix_questions_test_id'), 'questions', ['test_id'], unique=False)
    
    # Step 8: Recreate foreign key constraint with new name
    op.create_foreign_key(
        'questions_test_id_fkey',
        'questions', 'tests',
        ['test_id'], ['id']
    )


def downgrade() -> None:
    """Revert changes: rename tests table back to question_sets and test_id back to question_set_id."""
    # Step 1: Drop foreign key constraint
    op.drop_constraint('questions_test_id_fkey', 'questions', type_='foreignkey')
    
    # Step 2: Drop index on test_id
    op.drop_index(op.f('ix_questions_test_id'), table_name='questions')
    
    # Step 3: Rename the column back
    op.alter_column('questions', 'test_id', new_column_name='question_set_id')
    
    # Step 4: Rename the table back
    op.rename_table('tests', 'question_sets')
    
    # Step 5: Rename indexes back
    op.execute(sa.text("ALTER INDEX IF EXISTS ix_tests_id RENAME TO ix_question_sets_id"))
    op.execute(sa.text("ALTER INDEX IF EXISTS ix_tests_category_id RENAME TO ix_question_sets_category_id"))
    
    # Step 6: Rename foreign key constraint in question_sets table back
    connection = op.get_bind()
    try:
        connection.execute(sa.text("""
            ALTER TABLE question_sets 
            RENAME CONSTRAINT tests_category_id_fkey TO question_sets_category_id_fkey
        """))
    except:
        # Constraint might not exist or have different name, skip
        pass
    
    # Step 7: Create old index
    op.create_index(op.f('ix_questions_question_set_id'), 'questions', ['question_set_id'], unique=False)
    
    # Step 8: Recreate foreign key constraint with old name
    op.create_foreign_key(
        'questions_question_set_id_fkey',
        'questions', 'question_sets',
        ['question_set_id'], ['id']
    )
