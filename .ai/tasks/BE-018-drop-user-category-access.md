# BE-018 — Drop `user_category_access` Table

**Status:** TODO
**Layer:** Backend
**Risk Level:** Medium

---

## 1. Root Cause Analysis

### Context
The `user_category_access` table was used to grant individual users access to specific categories. This per-user assignment model is being replaced by the role-based permission system (`role_permissions`). The table and all application code referencing it must be removed.

### Affected Modules
- `app/models/` — ORM model for `user_category_access` (if it exists)
- `app/services/` — any service referencing category access checks
- `app/repository/` — any repository reading from this table
- `app/api/v1/` — any routes exposing category access management
- `app/models/users.py` — relationship `category_access` on User model
- `alembic/versions/x4y5z6a7b8c9_create_user_category_access_table.py` — reference only

---

## 2. Task Breakdown

---

### Task BE-018-A: Audit and Remove `user_category_access` Application Code

**Title:** Identify and delete all code referencing `user_category_access`

**Description:**
Perform a full grep audit of the codebase for references to `user_category_access`, `UserCategoryAccess`, and `category_access`. Remove all related files and references.

**Audit Targets (grep for):**
- `user_category_access`
- `UserCategoryAccess`
- `category_access`

**Expected Files to Delete (verify each exists first):**
- ORM model file (e.g., `app/models/user_category_access.py`)
- Repository file (e.g., `app/repository/user_category_access_repo.py`)
- Service file (e.g., `app/services/user_category_access_service.py`)
- Schema file (e.g., `app/schemas/user_category_access.py`)
- Route file (e.g., `app/api/v1/category_access.py`)

**Files to Update:**
- `app/models/users.py` — remove `category_access` relationship if present
- `app/models/__init__.py` — remove import
- `app/api/v1/__init__.py` — remove router registration
- Any permission or access-check service that queries this table

**Database Impact:** None in this task (handled in BE-018-B)

**API Changes:**
- Remove any endpoints related to `category_access` management (if they exist)

**Validation Rules:**
- After cleanup: no import error on application startup
- No reference to `user_category_access` or `UserCategoryAccess` remains in `app/`

**Acceptance Criteria:**
- Application starts without import errors
- Grep for `user_category_access` in `app/` returns zero results
- All authorization logic now routes exclusively through `role_permissions`

**Required Tests:**
- Run full test suite; update or remove any tests that tested category access assignment
- Confirm permission enforcement via `role_permissions` is unaffected

---

### Task BE-018-B: Drop `user_category_access` Table via Migration

**Title:** Create Alembic migration to DROP `user_category_access`

**Description:**
Create a new Alembic migration that drops the `user_category_access` table with a full downgrade path.

**Migration File:** new file in `alembic/versions/`

**Upgrade Logic:**
- Drop FK constraints referencing `user_category_access` (if any from other tables)
- `op.drop_table("user_category_access")`

**Downgrade Logic:**
- Recreate `user_category_access` table matching the schema from migration `x4y5z6a7b8c9_create_user_category_access_table.py`
- Recreate indexes and FK constraints

**Database Impact:**
- Table `user_category_access` and all its data permanently removed on upgrade

**Validation Rules:**
- Migration must be the correct `down_revision` in the chain (placed after BE-017-B migration)
- FK references from `users.id` must be handled correctly in downgrade

**Acceptance Criteria:**
- `alembic upgrade head` completes without error
- `SELECT * FROM user_category_access` → relation does not exist
- `alembic downgrade -1` recreates the table
- `alembic upgrade +1` re-drops it

**Required Tests:**
- Verify upgrade/downgrade cycle in local dev database
