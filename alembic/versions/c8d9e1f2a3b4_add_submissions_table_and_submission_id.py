"""add_submissions_table_and_submission_id

Revision ID: c8d9e1f2a3b4
Revises: bfcb0e742b83
Create Date: 2024-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c8d9e1f2a3b4'
down_revision: Union[str, Sequence[str], None] = 'bfcb0e742b83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create submissions table
    op.create_table(
        'submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('answer_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submissions_id'), 'submissions', ['id'], unique=False)
    
    # Create trigger for updated_at (PostgreSQL doesn't support ON UPDATE like MySQL)
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    op.execute("""
        CREATE TRIGGER update_submissions_updated_at 
        BEFORE UPDATE ON submissions 
        FOR EACH ROW 
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    # Add submission_id column to responses table (nullable first for existing data)
    op.add_column('responses', sa.Column('submission_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_responses_submission_id', 'responses', 'submissions', ['submission_id'], ['id'])


def downgrade() -> None:
    # Drop trigger and function
    op.execute("DROP TRIGGER IF EXISTS update_submissions_updated_at ON submissions;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    
    # Remove foreign key and column from responses table
    op.drop_constraint('fk_responses_submission_id', 'responses', type_='foreignkey')
    op.drop_column('responses', 'submission_id')
    
    # Drop submissions table
    op.drop_index(op.f('ix_submissions_id'), table_name='submissions')
    op.drop_table('submissions')

