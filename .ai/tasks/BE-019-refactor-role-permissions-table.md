# BE-019 — Refactor `role_permissions` Table

**Status:** TODO
**Layer:** Backend
**Risk Level:** Low

---

## 1. Root Cause Analysis

### Context
The `role_permissions` table currently has `created_at`, `name`, and `description` columns but is missing `updated_at` and `deleted_at`. Adding these columns aligns `role_permissions` with the soft-delete pattern used across all other models and enables permission soft-deletion without data loss.

### Affected Modules
- `app/models/roles.py` — `RolePermission` ORM model
- `app/schemas/` — Pydantic schemas for role permissions (response models)
- `app/repository/` — any query on `role_permissions` (must add `deleted_at IS NULL` filter)
- `alembic/versions/` — new DDL migration

---

## 2. Task Breakdown

---

### Task BE-019-A: Alembic Migration — Add `updated_at` and `deleted_at` to `role_permissions`

**Title:** Create migration to add `updated_at`, `deleted_at` columns to `role_permissions`

**Description:**
Add two new nullable timestamp columns to the `role_permissions` table:
- `updated_at`: auto-populated on row creation, updated on every change
- `deleted_at`: soft-delete marker; NULL means active record

**Migration File:** new file in `alembic/versions/`

**Upgrade Logic:**
```sql
ALTER TABLE role_permissions
  ADD COLUMN updated_at TIMESTAMP DEFAULT now(),
  ADD COLUMN deleted_at TIMESTAMP DEFAULT NULL;
```
- Existing rows should have `updated_at` backfilled to `created_at` value

**Downgrade Logic:**
```sql
ALTER TABLE role_permissions
  DROP COLUMN updated_at,
  DROP COLUMN deleted_at;
```

**Database Impact:**
- Schema-only change; no data deleted
- Existing rows: `updated_at` backfilled, `deleted_at` = NULL (all records remain active)

**Validation Rules:**
- `updated_at` must have `server_default=text("now()")` and `onupdate` trigger
- `deleted_at` must default to NULL
- Downgrade must remove both columns cleanly

**Acceptance Criteria:**
- `alembic upgrade head` → `\d role_permissions` shows `updated_at` and `deleted_at` columns
- Existing permission rows are unaffected (still active, `deleted_at = NULL`)
- `alembic downgrade -1` removes both columns

**Required Tests:**
- Verify migration upgrade/downgrade in local dev database

---

### Task BE-019-B: Update `RolePermission` ORM Model

**Title:** Add `updated_at` and `deleted_at` to `RolePermission` SQLAlchemy model

**Description:**
Update the `RolePermission` class in `app/models/roles.py` to reflect the new schema columns.

**Files Affected:**
- `app/models/roles.py`

**Changes:**
- Add `updated_at = Column(TIMESTAMP, server_default=text("now()"), onupdate=func.now())`
- Add `deleted_at = Column(TIMESTAMP, nullable=True, default=None)`

**Database Impact:** None (migration handled in BE-019-A)

**API Changes:** None

**Validation Rules:**
- Model must be consistent with SQLAlchemy conventions used in `User`, `Role` models

**Acceptance Criteria:**
- ORM model reflects new columns
- No import errors on application startup

**Required Tests:** None beyond startup validation

---

### Task BE-019-C: Enforce Soft-Delete Filter on `role_permissions` Queries

**Title:** Add `WHERE deleted_at IS NULL` filter to all `role_permissions` queries

**Description:**
Any repository or service that reads from `role_permissions` must be updated to exclude soft-deleted records. This ensures that deleted permissions are not accidentally enforced.

**Files to Audit and Update:**
- `app/services/permission_service.py` — `get_user_permissions()` and `check_permission()`
- `app/repository/` — any repo performing `.query(RolePermission)` or equivalent
- `app/api/v1/permissions.py` — list endpoints for role permissions (if exists)

**Change Pattern:**
```python
# Before
db.query(RolePermission).filter(RolePermission.role_id == role_id)

# After
db.query(RolePermission).filter(
    RolePermission.role_id == role_id,
    RolePermission.deleted_at.is_(None)
)
```

**Database Impact:** None

**API Changes:** None

**Validation Rules:**
- All queries on `role_permissions` must filter `deleted_at IS NULL`
- Soft-deleted permissions must not be enforced on any user

**Acceptance Criteria:**
- Manually set `deleted_at = now()` on a permission row → user loses that permission immediately
- Grep for `query(RolePermission)` and `select(RolePermission)` confirms all instances filter `deleted_at`

**Required Tests:**
- Unit test: soft-deleted permission is not returned by `get_user_permissions()`
- Unit test: active permission continues to be returned normally

---

### Task BE-019-D: Update Pydantic Schemas for `RolePermission`

**Title:** Add `updated_at` and `deleted_at` to role permission Pydantic response schemas

**Description:**
Update any Pydantic response model for `RolePermission` to optionally expose the new fields. Avoid breaking existing API consumers.

**Files Affected:**
- `app/schemas/` — locate role permission response schema (likely in `role_schema.py` or `permission_schema.py`)

**Changes:**
- Add `updated_at: datetime | None = None`
- Add `deleted_at: datetime | None = None`
- Both fields should be optional to avoid breaking existing clients

**API Changes:**
- GET role permissions response may now include `updated_at` and `deleted_at` (additive, non-breaking)

**Acceptance Criteria:**
- Response schema serializes new fields correctly
- Existing API responses remain valid (no removed fields)

**Required Tests:**
- Unit test: schema serialization includes new fields with correct types
