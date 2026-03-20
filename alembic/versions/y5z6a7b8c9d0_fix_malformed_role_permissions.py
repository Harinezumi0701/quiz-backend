"""fix_malformed_role_permissions

Revision ID: y5z6a7b8c9d0
Revises: x4y5z6a7b8c9
Create Date: 2026-03-20 00:02:00.000000

Fixes role permissions that were stored as comma-joined strings (e.g.
"tests::*,categories::*") instead of individual rows.  For each malformed
permission we insert the correct individual entries and then delete the
bad row.

Also ensures the three standard roles (admin, editor, user) have every
required permission present as a separate row.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'y5z6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'x4y5z6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Expected permissions per role name
ROLE_PERMISSIONS = {
    "admin":  ["*::*"],
    "editor": ["tests::*", "categories::*", "questions::*", "answers::*"],
    "user": [
        "categories::read",
        "tests::read",
        "questions::read",
        "user_tests::read",
        "profile::read",
        "profile::update",
        "dashboard::read",
    ],
}


def upgrade() -> None:
    conn = op.get_bind()

    # ------------------------------------------------------------------ #
    # Step 1 – split any comma-joined permission strings into individual  #
    #          rows, then remove the malformed original row.              #
    # ------------------------------------------------------------------ #
    malformed = conn.execute(
        sa.text(
            "SELECT id, role_id, permission "
            "FROM role_permissions "
            "WHERE permission LIKE '%,%'"
        )
    ).fetchall()

    for row in malformed:
        perm_id, role_id, raw_permission = row

        # Fetch already-valid individual permissions for this role so we
        # don't create duplicates.
        existing = {
            r[0]
            for r in conn.execute(
                sa.text(
                    "SELECT permission FROM role_permissions "
                    "WHERE role_id = :role_id AND id != :perm_id"
                ),
                {"role_id": role_id, "perm_id": perm_id},
            ).fetchall()
        }

        for part in raw_permission.split(","):
            part = part.strip()
            if part and part not in existing:
                conn.execute(
                    sa.text(
                        "INSERT INTO role_permissions (id, role_id, permission, created_at) "
                        "VALUES (uuidv7(), :role_id, :permission, NOW())"
                    ),
                    {"role_id": role_id, "permission": part},
                )
                existing.add(part)

        # Remove the malformed row
        conn.execute(
            sa.text("DELETE FROM role_permissions WHERE id = :id"),
            {"id": perm_id},
        )

    # ------------------------------------------------------------------ #
    # Step 2 – ensure every standard role has its required permissions.  #
    # ------------------------------------------------------------------ #
    for role_name, required_perms in ROLE_PERMISSIONS.items():
        role_row = conn.execute(
            sa.text(
                "SELECT id FROM roles WHERE name = :name AND deleted_at IS NULL LIMIT 1"
            ),
            {"name": role_name},
        ).fetchone()

        if not role_row:
            continue

        role_id = role_row[0]

        existing_perms = {
            r[0]
            for r in conn.execute(
                sa.text(
                    "SELECT permission FROM role_permissions WHERE role_id = :role_id"
                ),
                {"role_id": role_id},
            ).fetchall()
        }

        for permission in required_perms:
            if permission not in existing_perms:
                conn.execute(
                    sa.text(
                        "INSERT INTO role_permissions (id, role_id, permission, created_at) "
                        "VALUES (uuidv7(), :role_id, :permission, NOW())"
                    ),
                    {"role_id": role_id, "permission": permission},
                )


def downgrade() -> None:
    # Reversing data cleanup is not safe — permissions may have been further
    # modified after this migration ran.
    pass
