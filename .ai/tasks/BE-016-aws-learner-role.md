# BE-016 — Create `aws_learner` Role with Scoped Permissions

**Status:** TODO
**Layer:** Backend
**Risk Level:** Medium

---

## 1. Root Cause Analysis

### Context
A new role `aws_learner` must be introduced to grant users restricted access to AWS-related test content only (category `019c1ec6-47aa-76f7-9a68-035fd9314e6d`). The existing permission format `resource::action` must be extended to support a 3-part scoped format `resource::action::resource_id` to enforce category-level restrictions without user-specific assignment tables.

### Affected Modules
- `app/models/roles.py` — RolePermission model
- `app/services/permission_service.py` — permission matching logic
- `app/api/v1/tests.py` — test listing/retrieval endpoints
- `app/api/v1/questions.py` — question endpoints
- `app/api/v1/answers.py` — answer endpoints (if applicable)
- `alembic/versions/` — new seed migration

---

## 2. Task Breakdown

---

### Task BE-016-A: Extend Permission Matching to Support 3-Part Format

**Title:** Update `permission_service.py` to handle scoped permissions (`resource::action::id`)

**Description:**
The current permission system supports `resource::action` and wildcards (`*::*`, `resource::*`). A new 3-part format `resource::action::resource_id` must be supported to scope permissions to a specific entity (e.g., a category UUID). Matching logic must be updated without breaking existing 2-part permissions.

**Service/Modules Affected:**
- `app/services/permission_service.py`
  - `_permission_matches(pattern, permission)` — extend matching logic
  - `check_permission(db, user, required_permission)` — no change required
- `app/constants/permissions.py` — optionally add documentation comment for new format

**Database Impact:** None

**API Changes:** None

**Validation Rules:**
- `resource::action::id` format: exact match on all 3 parts
- Pattern `resource::*` must still match `resource::action::id` (wildcard action covers all scoped variants)
- Pattern `*::*` must still match `resource::action::id`
- Pattern `resource::action` (2-part) must NOT match `resource::action::id` (scoped) unless explicitly covered by wildcard

**Acceptance Criteria:**
- `_permission_matches("tests::read::019c...", "tests::read::019c...")` → True
- `_permission_matches("tests::*", "tests::read::019c...")` → True
- `_permission_matches("*::*", "tests::read::019c...")` → True
- `_permission_matches("tests::read", "tests::read::019c...")` → False (non-scoped does not cover scoped)
- Existing 2-part permission tests remain unaffected

**Required Tests:**
- Unit tests in `tests/` for `_permission_matches` covering all new format combinations
- Regression test confirming existing wildcard behavior unchanged

---

### Task BE-016-B: Enforce Category-Scoped Permissions on API Endpoints

**Title:** Add category-scoped permission checks to test, question, and answer endpoints

**Description:**
When a user has permission `tests::read::019c1ec6-47aa-76f7-9a68-035fd9314e6d`, they can only read tests belonging to that category. Endpoints for listing/retrieving tests, questions, and answers must check the scoped permission and filter or reject resources outside the permitted category.

**Service/Modules Affected:**
- `app/api/v1/tests.py` — GET list and GET by ID
- `app/api/v1/questions.py` — GET list and GET by ID
- `app/api/v1/answers.py` — GET list and GET by ID (if applicable)
- `app/services/permission_service.py` — add helper `get_permitted_category_ids(user_permissions, resource)` returning list of UUIDs or `None` (meaning unrestricted)
- `app/repository/test_repo.py`, `question_repo.py`, `answer_repo.py` — add optional `category_ids` filter parameter to list queries

**Database Impact:** None (filtering only, no schema change)

**API Changes:**
- No change to request/response format
- GET `/v1/tests` with `aws_learner` role returns only tests in permitted categories
- GET `/v1/tests/{id}` returns `403 Forbidden` if test category is not in user's permitted categories
- Same behavior for questions and answers

**Validation Rules:**
- Users with `*::*` or `tests::*` (unrestricted) see all tests → no category filter applied
- Users with only `tests::read::019c...` see only tests from that category
- Multiple scoped permissions (e.g., two category IDs) should be combined (OR logic)

**Acceptance Criteria:**
- `aws_learner` user GET `/v1/tests` returns only tests from `019c1ec6-47aa-76f7-9a68-035fd9314e6d`
- `aws_learner` user GET `/v1/tests/{id}` for a test outside the permitted category → `403 Forbidden`
- Admin user (`*::*`) sees all tests without category restriction
- Same enforcement for questions and answers

**Required Tests:**
- Integration test: aws_learner cannot access out-of-scope test
- Integration test: aws_learner can access in-scope test
- Integration test: admin can access any test

---

### Task BE-016-C: Seed `aws_learner` Role via Alembic Migration

**Title:** Create Alembic migration to seed `aws_learner` role and permissions

**Description:**
Add a new Alembic data migration (not DDL) that inserts the `aws_learner` role and its associated `role_permissions` rows. The migration must be reversible.

**Service/Modules Affected:**
- `alembic/versions/` — new migration file

**Database Impact:**
- INSERT into `roles`: name=`aws_learner`, description=`User allowed to take AWS-related tests only.`, default=False
- INSERT into `role_permissions` (8 rows):
  - `profile::read`
  - `profile::update`
  - `dashboard::read`
  - `submissions::create`
  - `tests::read::019c1ec6-47aa-76f7-9a68-035fd9314e6d`
  - `questions::read::019c1ec6-47aa-76f7-9a68-035fd9314e6d`
  - `answers::read::019c1ec6-47aa-76f7-9a68-035fd9314e6d`
  - `categories::read::019c1ec6-47aa-76f7-9a68-035fd9314e6d`

**Migration Downgrade Logic:**
- DELETE from `role_permissions` WHERE role_id = (SELECT id FROM roles WHERE name = 'aws_learner')
- DELETE from `roles` WHERE name = 'aws_learner'

**API Changes:** None

**Validation Rules:**
- Role name `aws_learner` must be unique; migration must check for existence before inserting to be idempotent
- Use `uuidv7()` or `uuid_generate_v4()` consistent with existing seed migrations (see `q7r8s9t0u1v2_add_rbac_tables_and_admin_role.py`)

**Acceptance Criteria:**
- After `alembic upgrade head`: `SELECT * FROM roles WHERE name = 'aws_learner'` returns 1 row
- After `alembic upgrade head`: `SELECT COUNT(*) FROM role_permissions WHERE role_id = <aws_learner_id>` returns 8
- After `alembic downgrade -1`: both rows are removed cleanly

**Required Tests:**
- Verify migration upgrade/downgrade without errors in local dev environment
