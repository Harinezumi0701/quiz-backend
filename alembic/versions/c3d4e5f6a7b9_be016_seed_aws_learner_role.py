"""be016_seed_aws_learner_role

Revision ID: c3d4e5f6a7b9
Revises: b2c3d4e5f6a8
Create Date: 2026-03-29 00:03:00.000000

Seeds the aws_learner role with the same read/submit permissions as the
default user role, but as a distinct non-default role.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b9'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AWS_LEARNER_PERMISSIONS = [
    "categories::read",
    "tests::read",
    "questions::read",
    "answers::read",
    "submissions::create",
    "dashboard::read",
    "user_tests::read",
    "profile::read",
    "profile::update",
]


def upgrade() -> None:
    conn = op.get_bind()

    # Skip if role already exists
    existing = conn.execute(
        sa.text("SELECT id FROM roles WHERE name = 'aws_learner' AND deleted_at IS NULL LIMIT 1")
    ).fetchone()
    if existing:
        return

    # Insert role
    conn.execute(
        sa.text(
            "INSERT INTO roles (id, name, description, \"default\", created_at, updated_at) "
            "VALUES (uuidv7(), 'aws_learner', 'AWS learner with read and quiz access', FALSE, NOW(), NOW())"
        )
    )

    role_row = conn.execute(
        sa.text("SELECT id FROM roles WHERE name = 'aws_learner' AND deleted_at IS NULL LIMIT 1")
    ).fetchone()
    role_id = role_row[0]

    for permission in AWS_LEARNER_PERMISSIONS:
        conn.execute(
            sa.text(
                "INSERT INTO role_permissions (id, role_id, permission, created_at, updated_at) "
                "VALUES (uuidv7(), :role_id, :permission, NOW(), NOW())"
            ),
            {"role_id": role_id, "permission": permission},
        )


def downgrade() -> None:
    conn = op.get_bind()

    role_row = conn.execute(
        sa.text("SELECT id FROM roles WHERE name = 'aws_learner' LIMIT 1")
    ).fetchone()
    if not role_row:
        return

    role_id = role_row[0]
    conn.execute(
        sa.text("DELETE FROM role_permissions WHERE role_id = :role_id"),
        {"role_id": role_id},
    )
    conn.execute(
        sa.text("DELETE FROM roles WHERE id = :role_id"),
        {"role_id": role_id},
    )
