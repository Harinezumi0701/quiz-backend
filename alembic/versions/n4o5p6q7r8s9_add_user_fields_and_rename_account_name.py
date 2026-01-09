"""add_user_fields_and_rename_account_name

Revision ID: n4o5p6q7r8s9
Revises: m3n4o5p6q7r8
Create Date: 2025-01-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'n4o5p6q7r8s9'
down_revision: Union[str, Sequence[str], None] = 'm3n4o5p6q7r8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename account_name to full_name and add new user fields."""
    # Rename account_name to full_name
    op.alter_column('users', 'account_name', new_column_name='full_name')
    
    # Add user_id column (unique, nullable=False, will be populated by application)
    op.add_column('users', sa.Column('user_id', sa.String(length=6), nullable=True, unique=True))
    
    # Add other new columns
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('birthday', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('address', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('job_title', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('company', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('join_date', sa.Date(), nullable=True))
    
    # Generate user_id for existing users
    # Create a function to generate user_id matching [A-Za-z\._-]{6}
    connection = op.get_bind()
    connection.execute(sa.text("""
        CREATE OR REPLACE FUNCTION generate_user_id() RETURNS TEXT AS $$
        DECLARE
            chars TEXT := 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._-';
            result TEXT := '';
            i INTEGER;
        BEGIN
            FOR i IN 1..6 LOOP
                result := result || SUBSTRING(chars, FLOOR(1 + RANDOM() * LENGTH(chars))::INTEGER, 1);
            END LOOP;
            RETURN result;
        END;
        $$ LANGUAGE plpgsql;
    """))
    
    # Generate unique user_id for existing users
    connection.execute(sa.text("""
        DO $$
        DECLARE
            u RECORD;
            new_user_id TEXT;
            attempts INTEGER;
        BEGIN
            FOR u IN SELECT id FROM users WHERE user_id IS NULL LOOP
                attempts := 0;
                LOOP
                    new_user_id := generate_user_id();
                    EXIT WHEN NOT EXISTS (SELECT 1 FROM users WHERE user_id = new_user_id);
                    attempts := attempts + 1;
                    IF attempts > 100 THEN
                        RAISE EXCEPTION 'Unable to generate unique user_id after 100 attempts';
                    END IF;
                END LOOP;
                UPDATE users SET user_id = new_user_id WHERE id = u.id;
            END LOOP;
        END $$;
    """))
    
    # Drop the temporary function
    connection.execute(sa.text("DROP FUNCTION IF EXISTS generate_user_id();"))
    
    # Now make user_id NOT NULL
    op.alter_column('users', 'user_id', nullable=False)


def downgrade() -> None:
    """Revert changes: rename full_name back to account_name and remove new fields."""
    # Remove new columns
    op.drop_column('users', 'join_date')
    op.drop_column('users', 'company')
    op.drop_column('users', 'job_title')
    op.drop_column('users', 'address')
    op.drop_column('users', 'birthday')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'user_id')
    
    # Rename full_name back to account_name
    op.alter_column('users', 'full_name', new_column_name='account_name')
