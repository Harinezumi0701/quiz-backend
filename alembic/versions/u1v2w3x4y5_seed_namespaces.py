"""seed_namespaces

Revision ID: u1v2w3x4y5
Revises: t0u1v2w3x4
Create Date: 2025-01-17 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'u1v2w3x4y5'
down_revision: Union[str, Sequence[str], None] = 't0u1v2w3x4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed namespaces table with default data."""
    namespaces_data = [
        {
            'name': 'Categories',
            'description': 'Category management namespace',
            'prefix': 'categories',
        },
        {
            'name': 'Tests',
            'description': 'Test management namespace',
            'prefix': 'tests',
        },
        {
            'name': 'Questions',
            'description': 'Question management namespace',
            'prefix': 'questions',
        },
        {
            'name': 'Answers',
            'description': 'Answer management namespace',
            'prefix': 'answers',
        },
        {
            'name': 'Users',
            'description': 'User management namespace',
            'prefix': 'users',
        },
        {
            'name': 'Roles',
            'description': 'Role management namespace',
            'prefix': 'roles',
        },
        {
            'name': 'Permissions',
            'description': 'Permission management namespace',
            'prefix': 'permissions',
        },
    ]

    # Insert namespaces using raw SQL to handle UUID generation
    connection = op.get_bind()
    for namespace in namespaces_data:
        connection.execute(
            sa.text("""
                INSERT INTO namespaces (id, name, description, prefix, created_at, updated_at)
                VALUES (uuidv7(), :name, :description, :prefix, NOW(), NOW())
                ON CONFLICT (prefix) DO NOTHING
            """),
            {
                'name': namespace['name'],
                'description': namespace['description'],
                'prefix': namespace['prefix'],
            }
        )


def downgrade() -> None:
    """Remove seeded namespaces."""
    op.execute(
        sa.text("""
            DELETE FROM namespaces 
            WHERE prefix IN ('categories', 'tests', 'questions', 'answers', 'users', 'roles', 'permissions')
        """)
    )
