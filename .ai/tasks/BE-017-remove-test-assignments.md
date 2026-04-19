# BE-017 — Remove Test Assignment System

**Status:** TODO
**Layer:** Backend
**Risk Level:** High

---

## 1. Root Cause Analysis

### Context
The test assignment system (`user_test_assignments` table, related ORM model, schemas, service, repository, and API routes) is being replaced by the role-based permission system. All assignment-related code must be removed and the table must be dropped via a reversible Alembic migration.

### Affected Modules
- `app/api/v1/test_assignments.py`
- `app/services/user_test_assignment_service.py`
- `app/repository/user_test_assignment_repo.py`
- `app/models/user_test_assignments.py`
- `app/schemas/user_test_assignment.py`
- `app/api/v1/__init__.py` or router registration file
- `alembic/versions/v2w3x4y5z6a7_create_user_test_assignments_table.py` — reference only (do not modify; create new DROP migration)
- Any service that cross-references `UserTestAssignment` (e.g., `user_tests`, `submissions`)

---

## 2. Task Breakdown

---

### Task BE-017-A: Remove Test Assignment Code

**Title:** Delete all test assignment application code

**Description:**
Remove all Python source files related to the test assignment feature. Audit all remaining files for any import or reference to these deleted modules and clean them up.

**Files to Delete:**
- `app/api/v1/test_assignments.py`
- `app/services/user_test_assignment_service.py`
- `app/repository/user_test_assignment_repo.py`
- `app/models/user_test_assignments.py`
- `app/schemas/user_test_assignment.py`

**Files to Audit and Update:**
- `app/api/v1/__init__.py` (or equivalent router registration) — remove `test_assignments` router include
- `app/models/__init__.py` — remove `UserTestAssignment` import
- `app/schemas/__init__.py` — remove assignment schema imports
- Any service importing `user_test_assignment_repo` or `UserTestAssignment` (grep codebase)

**Database Impact:** None in this task (handled in BE-017-B)

**API Changes:**
- Remove endpoints:
  - `GET /v1/test-assignments`
  - `POST /v1/test-assignments`
  - `POST /v1/test-assignments/bulk`
  - `DELETE /v1/test-assignments/{id}`

**Validation Rules:**
- After removal, `python -c "from app.api.v1 import router"` must succeed without import errors
- No reference to `UserTestAssignment`, `user_test_assignments`, or `test_assignment` remains in `app/` source

**Acceptance Criteria:**
- Application starts cleanly with no import errors
- All removed endpoints return `404 Not Found`
- No dangling references in surviving code files

**Required Tests:**
- Run full test suite after deletion; fix any test files that imported assignment modules
- Delete or skip test files in `tests/` covering test assignments

---

### Task BE-017-B: Drop `user_test_assignments` Table via Migration

**Title:** Create Alembic migration to DROP `user_test_assignments`

**Description:**
Create a new Alembic migration that drops the `user_test_assignments` table, its indexes, foreign keys, and unique constraints. The migration must include a full downgrade path to recreate the table.

**Migration File:** new file in `alembic/versions/`

**Upgrade Logic (DROP):**
```sql
DROP TABLE IF EXISTS user_test_assignments;
```
(Alembic will handle FK cascade; ensure `op.drop_table` is used after dropping constraints if needed)

**Downgrade Logic (RECREATE):**
```sql
CREATE TABLE user_test_assignments (
  id UUID PRIMARY KEY DEFAULT uuidv7(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  test_id UUID NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
  assigned_at TIMESTAMP DEFAULT now(),
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  deleted_at TIMESTAMP,
  UNIQUE(user_id, test_id)
);
CREATE INDEX ON user_test_assignments(id, user_id, test_id);
```

**Database Impact:**
- Table `user_test_assignments` and all its data permanently removed on upgrade

**Validation Rules:**
- Migration must depend on the last migration in the chain (set correct `down_revision`)
- Downgrade must fully recreate the table to the state matching the original migration

**Acceptance Criteria:**
- `alembic upgrade head` completes without error
- `SELECT * FROM user_test_assignments` → relation does not exist
- `alembic downgrade -1` recreates the table cleanly
- `alembic upgrade +1` re-drops it cleanly

**Required Tests:**
- Verify upgrade/downgrade cycle in local dev database
