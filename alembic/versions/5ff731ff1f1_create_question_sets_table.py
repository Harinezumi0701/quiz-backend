"""create_question_sets_table

Revision ID: 5ff731ff1f1
Revises: 8e64cf816f4f
Create Date: 2025-01-15 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5ff731ff1f1'
down_revision: Union[str, Sequence[str], None] = '8e64cf816f4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create question_sets table and migrate data from questions.question_set."""
    # Step 1: Create question_sets table
    op.create_table(
        'question_sets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuidv7()')),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_sets_id'), 'question_sets', ['id'], unique=False)
    op.create_index(op.f('ix_question_sets_category_id'), 'question_sets', ['category_id'], unique=False)

    # Step 2: Migrate data from questions.question_set to question_sets
    # Get all unique question_set values with their category_id
    connection = op.get_bind()
    
    # Find all unique question_set values with their category_id
    result = connection.execute(sa.text("""
        SELECT DISTINCT q.question_set, q.category_id
        FROM questions q
        WHERE q.question_set IS NOT NULL
        AND q.deleted_at IS NULL
    """))
    
    # Create question_sets records
    for row in result:
        question_set_name = row[0]
        category_id = row[1]
        
        # Insert into question_sets if not exists
        connection.execute(sa.text("""
            INSERT INTO question_sets (id, name, category_id, created_at, updated_at)
            SELECT uuidv7(), :name, :category_id, NOW(), NOW()
            WHERE NOT EXISTS (
                SELECT 1 FROM question_sets 
                WHERE name = :name AND category_id = :category_id
            )
        """), {"name": question_set_name, "category_id": category_id})
    
    # Step 3: Add question_set_id column to questions table
    op.add_column('questions', sa.Column('question_set_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_questions_question_set_id'), 'questions', ['question_set_id'], unique=False)

    # Step 4: Update questions.question_set_id based on question_set name and category_id
    connection.execute(sa.text("""
        UPDATE questions q
        SET question_set_id = qs.id
        FROM question_sets qs
        WHERE q.question_set = qs.name
        AND q.category_id = qs.category_id
        AND q.question_set IS NOT NULL
        AND q.deleted_at IS NULL
    """))

    # Step 5: Add foreign key constraint
    op.create_foreign_key(
        'questions_question_set_id_fkey',
        'questions', 'question_sets',
        ['question_set_id'], ['id']
    )

    # Step 6: Drop the old question_set column
    op.drop_column('questions', 'question_set')


def downgrade() -> None:
    """Revert changes: restore question_set column and drop question_sets table."""
    # Step 1: Add back question_set column
    op.add_column('questions', sa.Column('question_set', sa.String(length=100), nullable=True))

    # Step 2: Migrate data back from question_sets to questions.question_set
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE questions q
        SET question_set = qs.name
        FROM question_sets qs
        WHERE q.question_set_id = qs.id
    """))

    # Step 3: Drop foreign key constraint
    op.drop_constraint('questions_question_set_id_fkey', 'questions', type_='foreignkey')

    # Step 4: Drop index and column
    op.drop_index(op.f('ix_questions_question_set_id'), table_name='questions')
    op.drop_column('questions', 'question_set_id')

    # Step 5: Drop question_sets table
    op.drop_index(op.f('ix_question_sets_category_id'), table_name='question_sets')
    op.drop_index(op.f('ix_question_sets_id'), table_name='question_sets')
    op.drop_table('question_sets')
