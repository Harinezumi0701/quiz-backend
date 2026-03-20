"""seed_default_roles

Revision ID: w3x4y5z6a7b8
Revises: v2w3x4y5z6a7
Create Date: 2026-03-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'w3x4y5z6a7b8'
down_revision: Union[str, Sequence[str], None] = 'v2w3x4y5z6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _upsert_role_with_permissions(conn, name: str, description: str, default: bool, permissions: list[str]) -> None:
    """
    Idempotent upsert: create the role if it doesn't exist, then ensure each
    required permission exists as an individual row. Pre-existing permissions
    (including any malformed comma-joined ones) are left untouched — only the
    missing individual permissions are inserted.
    """
    # Get existing role or create it
    result = conn.execute(
        sa.text("SELECT id FROM roles WHERE name = :name AND deleted_at IS NULL LIMIT 1"),
        {"name": name},
    )
    row = result.fetchone()

    if row:
        role_id = row[0]
    else:
        result = conn.execute(
            sa.text("""
                INSERT INTO roles (id, name, description, "default", created_at, updated_at)
                VALUES (uuidv7(), :name, :description, :default, NOW(), NOW())
                RETURNING id
            """),
            {"name": name, "description": description, "default": default},
        )
        role_id = result.scalar()

    # Fetch already-stored permission strings for this role
    existing = conn.execute(
        sa.text("SELECT permission FROM role_permissions WHERE role_id = :role_id"),
        {"role_id": role_id},
    ).fetchall()
    existing_perms = {row[0] for row in existing}

    # Insert only the individual permissions that are not yet present
    for permission in permissions:
        if permission not in existing_perms:
            conn.execute(
                sa.text("""
                    INSERT INTO role_permissions (id, role_id, permission, created_at)
                    VALUES (uuidv7(), :role_id, :permission, NOW())
                """),
                {"role_id": role_id, "permission": permission},
            )


def upgrade() -> None:
    conn = op.get_bind()

    # Admin role — full access
    _upsert_role_with_permissions(
        conn,
        name="admin",
        description="Administrator with full permissions",
        default=False,
        permissions=["*::*"],
    )

    # Editor role — manages content
    _upsert_role_with_permissions(
        conn,
        name="editor",
        description="Editor with access to tests, categories, questions, and answers",
        default=False,
        permissions=[
            "tests::*",
            "categories::*",
            "questions::*",
            "answers::*",
        ],
    )

    # User role — read-only learner access (default role)
    _upsert_role_with_permissions(
        conn,
        name="user",
        description="Standard user with read access to learning content",
        default=True,
        permissions=[
            "categories::read",
            "tests::read",
            "questions::read",
            "user_tests::read",
            "profile::read",
            "profile::update",
            "dashboard::read",
        ],
    )


def downgrade() -> None:
    # Do not delete roles on downgrade — they may be assigned to users.
    pass
