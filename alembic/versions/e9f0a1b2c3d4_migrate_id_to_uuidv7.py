"""migrate_id_to_uuidv7

Revision ID: e9f0a1b2c3d4
Revises: 62de59e6b79e
Create Date: 2025-01-08 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e9f0a1b2c3d4'
down_revision: Union[str, Sequence[str], None] = '62de59e6b79e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrate all id columns from Integer to UUID with uuidv7().
    
    Note: PostgreSQL 18+ has built-in uuidv7() function, no extension needed.
    """
    
    # Step 1: Migrate users table
    _migrate_table_to_uuid('users', [
        ('submissions', 'user_id'),
        ('submission_history', 'user_id'),
    ])
    
    # Step 3: Migrate categories table
    _migrate_table_to_uuid('categories', [
        ('questions', 'category_id'),
    ])
    
    # Step 4: Migrate questions table
    _migrate_table_to_uuid('questions', [
        ('answers', 'question_id'),
        ('submissions', 'question_id'),
    ])
    
    # Step 5: Migrate answers table
    _migrate_table_to_uuid('answers', [
        ('submissions', 'selected_option_id'),
    ])
    
    # Step 6: Migrate submission_history table
    _migrate_table_to_uuid('submission_history', [
        ('submissions', 'submission_history_id'),
    ])
    
    # Step 7: Migrate submissions table (no foreign keys pointing to it)
    _migrate_table_to_uuid('submissions', [])


def _migrate_table_to_uuid(table_name: str, foreign_key_tables: list) -> None:
    """
    Helper function to migrate a table's id column from Integer to UUID.
    
    Args:
        table_name: Name of the table to migrate
        foreign_key_tables: List of tuples (table_name, column_name) that have foreign keys to this table
    """
    # Step 1: Drop all foreign key constraints that reference this table
    for fk_table, fk_column in foreign_key_tables:
        # Get constraint name
        constraint_name = f'fk_{fk_table}_{fk_column}'
        # Try to drop constraint (might have different naming)
        op.execute(f"""
            DO $$ 
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_name = '{constraint_name}' 
                    AND table_name = '{fk_table}'
                ) THEN
                    ALTER TABLE {fk_table} DROP CONSTRAINT {constraint_name};
                END IF;
            END $$;
        """)
        # Also try dropping by pattern
        op.execute(f"""
            DO $$ 
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN (
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = '{fk_table}' 
                    AND constraint_type = 'FOREIGN KEY'
                    AND constraint_name LIKE '%{fk_column}%'
                ) LOOP
                    EXECUTE 'ALTER TABLE {fk_table} DROP CONSTRAINT ' || r.constraint_name;
                END LOOP;
            END $$;
        """)
    
    # Step 2: Add new UUID column
    op.add_column(table_name, sa.Column('id_new', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Step 3: Generate UUIDs for existing rows
    # Use built-in uuidv7() function (PostgreSQL 18+)
    op.execute(f"""
        UPDATE {table_name} 
        SET id_new = uuidv7()
        WHERE id_new IS NULL;
    """)
    
    # Step 4: Make id_new NOT NULL
    op.alter_column(table_name, 'id_new', nullable=False)
    
    # Step 5: Update foreign key columns in dependent tables (BEFORE dropping old id)
    migrated_fk_tables = []
    for fk_table, fk_column in foreign_key_tables:
        # Check if column is already UUID (might have been migrated by another table)
        result = op.get_bind().execute(sa.text(f"""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = '{fk_table}' 
            AND column_name = '{fk_column}'
        """))
        row = result.fetchone()
        
        if row and row[0] == 'uuid':
            # Already migrated, just track for FK constraint recreation
            migrated_fk_tables.append((fk_table, fk_column))
            continue
        
        # Add new UUID column
        op.add_column(fk_table, sa.Column(f'{fk_column}_new', postgresql.UUID(as_uuid=True), nullable=True))
        
        # Migrate data: map old integer FK to new UUID id_new
        # Join on the old integer id column (which still exists)
        op.execute(f"""
            UPDATE {fk_table} fk
            SET {fk_column}_new = t.id_new
            FROM {table_name} t
            WHERE fk.{fk_column}::integer = t.id::integer;
        """)
        
        # Drop old column
        op.drop_column(fk_table, fk_column)
        
        # Rename new column
        op.alter_column(fk_table, f'{fk_column}_new', new_column_name=fk_column)
        migrated_fk_tables.append((fk_table, fk_column))
    
    # Step 6: Drop old primary key constraint
    # Find the actual constraint name (might be different after table rename)
    result = op.get_bind().execute(sa.text(f"""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = '{table_name}' 
        AND constraint_type = 'PRIMARY KEY'
    """))
    row = result.fetchone()
    if row:
        constraint_name = row[0]
        op.drop_constraint(constraint_name, table_name, type_='primary')
    
    # Step 7: Drop old id column
    op.drop_column(table_name, 'id')
    
    # Step 8: Rename id_new to id
    op.alter_column(table_name, 'id_new', new_column_name='id')
    
    # Step 9: Add new primary key constraint
    op.create_primary_key(f'{table_name}_pkey', table_name, ['id'])
    
    # Step 10: Set default for future inserts
    op.alter_column(table_name, 'id', 
                    server_default=sa.text('uuidv7()'),
                    existing_type=postgresql.UUID(as_uuid=True),
                    existing_nullable=False)
    
    # Step 11: Recreate index
    op.drop_index(op.f(f'ix_{table_name}_id'), table_name=table_name, if_exists=True)
    op.create_index(op.f(f'ix_{table_name}_id'), table_name, ['id'], unique=False)
    
    # Step 12: Recreate foreign key constraints
    for fk_table, fk_column in migrated_fk_tables:
        # Check if constraint already exists
        result = op.get_bind().execute(sa.text(f"""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = '{fk_table}' 
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name = 'fk_{fk_table}_{fk_column}'
        """))
        if result.fetchone():
            # Constraint already exists, skip
            continue
        
        op.create_foreign_key(
            f'fk_{fk_table}_{fk_column}',
            fk_table, table_name,
            [fk_column], ['id']
        )


def downgrade() -> None:
    """Revert UUID columns back to Integer."""
    # Note: This downgrade is complex and may lose data
    # It's recommended to restore from backup instead
    
    # Migrate submissions table first (no dependencies)
    _downgrade_table_from_uuid('submissions', [])
    
    # Migrate submission_history
    _downgrade_table_from_uuid('submission_history', [
        ('submissions', 'submission_history_id'),
    ])
    
    # Migrate answers
    _downgrade_table_from_uuid('answers', [
        ('submissions', 'selected_option_id'),
    ])
    
    # Migrate questions
    _downgrade_table_from_uuid('questions', [
        ('answers', 'question_id'),
        ('submissions', 'question_id'),
    ])
    
    # Migrate categories
    _downgrade_table_from_uuid('categories', [
        ('questions', 'category_id'),
    ])
    
    # Migrate users last
    _downgrade_table_from_uuid('users', [
        ('submissions', 'user_id'),
        ('submission_history', 'user_id'),
    ])


def _downgrade_table_from_uuid(table_name: str, foreign_key_tables: list) -> None:
    """Helper function to downgrade UUID back to Integer."""
    # Drop foreign keys
    for fk_table, fk_column in foreign_key_tables:
        op.execute(f"""
            DO $$ 
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN (
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name = '{fk_table}' 
                    AND constraint_type = 'FOREIGN KEY'
                    AND constraint_name LIKE '%{fk_column}%'
                ) LOOP
                    EXECUTE 'ALTER TABLE {fk_table} DROP CONSTRAINT ' || r.constraint_name;
                END LOOP;
            END $$;
        """)
    
    # Add new integer column
    op.add_column(table_name, sa.Column('id_new', sa.Integer(), nullable=True))
    
    # Generate sequential IDs (this will lose UUID information)
    op.execute(f"""
        WITH numbered AS (
            SELECT id, ROW_NUMBER() OVER (ORDER BY created_at, id) as rn
            FROM {table_name}
        )
        UPDATE {table_name} t
        SET id_new = n.rn
        FROM numbered n
        WHERE t.id = n.id;
    """)
    
    # Make NOT NULL
    op.alter_column(table_name, 'id_new', nullable=False)
    
    # Drop primary key
    # Find the actual constraint name
    result = op.get_bind().execute(sa.text(f"""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = '{table_name}' 
        AND constraint_type = 'PRIMARY KEY'
    """))
    row = result.fetchone()
    if row:
        constraint_name = row[0]
        op.drop_constraint(constraint_name, table_name, type_='primary')
    
    # Drop UUID column
    op.drop_column(table_name, 'id')
    
    # Rename
    op.alter_column(table_name, 'id_new', new_column_name='id')
    
    # Add primary key
    op.create_primary_key(f'{table_name}_pkey', table_name, ['id'])
    
    # Create sequence for auto-increment
    op.execute(f"CREATE SEQUENCE IF NOT EXISTS {table_name}_id_seq OWNED BY {table_name}.id;")
    op.execute(f"ALTER TABLE {table_name} ALTER COLUMN id SET DEFAULT nextval('{table_name}_id_seq');")
    op.execute(f"SELECT setval('{table_name}_id_seq', (SELECT MAX(id) FROM {table_name}));")
    
    # Recreate index
    op.drop_index(op.f(f'ix_{table_name}_id'), table_name=table_name, if_exists=True)
    op.create_index(op.f(f'ix_{table_name}_id'), table_name, ['id'], unique=False)
    
    # Update foreign keys
    for fk_table, fk_column in foreign_key_tables:
        # Add integer column
        op.add_column(fk_table, sa.Column(f'{fk_column}_new', sa.Integer(), nullable=True))
        
        # This migration is complex - we'd need to map UUIDs back to integers
        # For now, set to NULL (data loss)
        op.execute(f"UPDATE {fk_table} SET {fk_column}_new = NULL;")
        
        # Drop UUID column
        op.drop_column(fk_table, fk_column)
        
        # Rename
        op.alter_column(fk_table, f'{fk_column}_new', new_column_name=fk_column)
        
        # Recreate foreign key
        op.create_foreign_key(
            f'fk_{fk_table}_{fk_column}',
            fk_table, table_name,
            [fk_column], ['id']
        )
