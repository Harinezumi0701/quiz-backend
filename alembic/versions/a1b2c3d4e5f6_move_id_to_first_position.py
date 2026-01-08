"""move_id_to_first_position

Revision ID: a1b2c3d4e5f6
Revises: f0a1b2c3d4e5
Create Date: 2025-01-08 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f0a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Move id primary key column to the first position in all tables.
    
    PostgreSQL doesn't support changing column order directly. This migration
    recreates each table with id first by building the table definition manually.
    
    Tables processed:
    - users
    - categories
    - questions
    - answers
    - submissions
    - submission_history
    """
    
    # Process tables in reverse dependency order
    tables = ['submissions', 'submission_history', 'answers', 'questions', 'categories', 'users']
    
    for table_name in tables:
        _recreate_table_with_id_first(table_name)


def _recreate_table_with_id_first(table_name: str) -> None:
    """Recreate table with id column first."""
    
    # Check if id is already first
    check_result = op.get_bind().execute(sa.text(f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
        LIMIT 1
    """))
    
    first_col = check_result.fetchone()
    if first_col and first_col[0] == 'id':
        # Already in first position
        return
    
    # Get all columns with full definitions
    cols_result = op.get_bind().execute(sa.text(f"""
        SELECT 
            a.attname as column_name,
            pg_catalog.format_type(a.atttypid, a.atttypmod) as data_type,
            a.attnotnull as not_null,
            pg_get_expr(d.adbin, d.adrelid) as default_value,
            a.attnum as ordinal_position
        FROM pg_catalog.pg_attribute a
        LEFT JOIN pg_catalog.pg_attrdef d ON (a.attrelid, a.attnum) = (d.adrelid, d.adnum)
        WHERE a.attrelid = '{table_name}'::regclass
        AND a.attnum > 0
        AND NOT a.attisdropped
        ORDER BY a.attnum
    """))
    
    all_cols = cols_result.fetchall()
    if not all_cols:
        return
    
    # Separate id column from others
    id_col = None
    other_cols = []
    for col in all_cols:
        if col[0] == 'id':
            id_col = col
        else:
            other_cols.append(col)
    
    if not id_col:
        return
    
    # Get primary key constraint name
    pk_result = op.get_bind().execute(sa.text(f"""
        SELECT constraint_name
        FROM information_schema.table_constraints
        WHERE table_name = '{table_name}'
        AND constraint_type = 'PRIMARY KEY'
    """))
    pk_row = pk_result.fetchone()
    pk_name = pk_row[0] if pk_row else f'{table_name}_pkey'
    
    # Build column definitions with id first
    col_defs = []
    
    # Add id column first
    id_def = f'id {id_col[1]}'
    if id_col[2]:  # not_null
        id_def += ' NOT NULL'
    if id_col[3]:  # default_value
        id_def += f' DEFAULT {id_col[3]}'
    col_defs.append(id_def)
    
    # Add other columns
    for col in other_cols:
        col_def = f'{col[0]} {col[1]}'
        if col[2]:  # not_null
            col_def += ' NOT NULL'
        if col[3]:  # default_value
            col_def += f' DEFAULT {col[3]}'
        col_defs.append(col_def)
    
    # Create new table with correct column order
    temp_table = f'{table_name}_reordered'
    create_sql = f"CREATE TABLE {temp_table} ({', '.join(col_defs)})"
    op.execute(create_sql)
    
    # Copy data - need to specify all columns in order
    all_col_names = [col[0] for col in all_cols]
    # Reorder: id first, then others
    reordered_col_names = ['id'] + [c for c in all_col_names if c != 'id']
    
    # Build INSERT statement
    insert_cols = ', '.join(reordered_col_names)
    op.execute(f"""
        INSERT INTO {temp_table} ({insert_cols})
        SELECT {insert_cols} FROM {table_name}
    """)
    
    # Drop old table (CASCADE to handle dependencies)
    op.execute(f"DROP TABLE {table_name} CASCADE")
    
    # Rename new table
    op.rename_table(temp_table, table_name)
    
    # Recreate primary key
    op.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {pk_name} PRIMARY KEY (id)")
    
    # Note: Foreign keys, indexes, and triggers from other tables
    # that reference this table will need to be recreated manually if needed


def downgrade() -> None:
    """Revert column order.
    
    Note: Column order doesn't affect database functionality in PostgreSQL.
    This downgrade is a no-op as the original order cannot be reliably restored.
    """
    pass
