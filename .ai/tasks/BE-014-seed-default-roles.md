---
id: BE-014
title: Seed predefined roles — Admin, Editor, User
spec: spec/02-auth-rbac.md#role--permission-model
status: todo
priority: high
---

## Context
The RBAC infrastructure (Role, RolePermission models, permission matching) is in place but the system has no predefined roles. Per the RBAC spec, three standard roles must exist out of the box: **Admin**, **Editor**, and **User** (default). Without seeding, a freshly deployed system cannot enforce the permission matrix.

## Acceptance Criteria
- [ ] Seed script or Alembic data migration creates 3 roles idempotently (skip if name already exists):
  - **Admin** — permission `*::*`; `default=False`
  - **Editor** — permissions `tests::*`, `categories::*`, `questions::*`, `answers::*`; `default=False`
  - **User** — permissions `categories::read`, `tests::read`, `questions::read`, `user_tests::read`, `profile::read`, `profile::update`, `dashboard::read`; `default=True`
- [ ] `DEFAULT_USER_PERMISSIONS` in `app/constants/permissions.py` matches the User role permission list above
- [ ] Running the seed twice does not create duplicate roles or permissions
- [ ] Existing users without a `role_id` fall back to `DEFAULT_USER_PERMISSIONS` (existing behavior preserved)

## Technical Notes
- Preferred approach: Alembic data migration (`alembic revision -m "seed_default_roles"`) using `op.execute()` or bulk inserts via SQLAlchemy session
- Alternative: standalone `scripts/seed_roles.py` script callable via `python scripts/seed_roles.py`
- Check uniqueness by `Role.name` before inserting
- Affected files:
  - `app/models/roles.py` — Role & RolePermission models
  - `app/constants/permissions.py` — `DEFAULT_USER_PERMISSIONS` constant
  - `alembic/versions/` — new data migration file
  - `scripts/` — optional seed script
