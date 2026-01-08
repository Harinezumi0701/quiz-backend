"""add_categories_table

Revision ID: 62de59e6b79e
Revises: c8d9e1f2a3b4
Create Date: 2025-01-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '62de59e6b79e'
down_revision: Union[str, Sequence[str], None] = 'd7e8f9a0b1c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Create categories table and migrate data."""
    # Step 1: Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=True)
    
    # Step 2: Create trigger for updated_at on categories table
    op.execute("""
        CREATE TRIGGER update_categories_updated_at 
        BEFORE UPDATE ON categories 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    # Step 3: Migrate unique category names from questions to categories table
    op.execute("""
        INSERT INTO categories (name, created_at, updated_at)
        SELECT DISTINCT category, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        FROM questions
        WHERE category IS NOT NULL
        AND deleted_at IS NULL
        ON CONFLICT (name) DO NOTHING;
    """)
    
    # Step 4: Add category_id column to questions table (nullable first)
    op.add_column('questions', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_questions_category_id'), 'questions', ['category_id'], unique=False)
    
    # Step 5: Update category_id in questions table based on category name
    op.execute("""
        UPDATE questions q
        SET category_id = c.id
        FROM categories c
        WHERE q.category = c.name
        AND q.deleted_at IS NULL;
    """)
    
    # Step 6: Create foreign key constraint
    op.create_foreign_key(
        'fk_questions_category_id',
        'questions', 'categories',
        ['category_id'], ['id']
    )
    
    # Step 7: Drop old category column (keep it for now in case of rollback, but mark as deprecated)
    # We'll keep the column for backward compatibility during transition
    # op.drop_column('questions', 'category')


def downgrade() -> None:
    """Downgrade schema: Revert to string-based category."""
    # Step 1: Add back category column if it was dropped
    # op.add_column('questions', sa.Column('category', sa.String(length=100), nullable=True))
    
    # Step 2: Update category column from categories table
    op.execute("""
        UPDATE questions q
        SET category = c.name
        FROM categories c
        WHERE q.category_id = c.id;
    """)
    
    # Step 3: Drop foreign key constraint
    op.drop_constraint('fk_questions_category_id', 'questions', type_='foreignkey')
    
    # Step 4: Drop index and column
    op.drop_index(op.f('ix_questions_category_id'), table_name='questions')
    op.drop_column('questions', 'category_id')
    
    # Step 5: Drop trigger
    op.execute("DROP TRIGGER IF EXISTS update_categories_updated_at ON categories;")
    
    # Step 6: Drop categories table
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
