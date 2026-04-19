---
id: BE-015
title: Category-based test access for User role
spec: spec/02-auth-rbac.md#special-handling-user-role
status: todo
priority: high
---

## Context
Per the RBAC spec, users with the **User** role may only access tests belonging to categories they have been explicitly granted access to. Currently `GET /api/v1/tests` returns all tests to anyone with `tests::read`. A `user_category_access` intermediate table and filtering logic are needed to enforce category-scoped visibility. Additionally, test submission must verify that the user has an active assignment for the test.

## Acceptance Criteria
- [ ] New model `UserCategoryAccess`: `id` (UUIDv7), `user_id` (FK → users), `category_id` (FK → categories), `created_at`; unique constraint on `(user_id, category_id)`
- [ ] Alembic migration for the new table
- [ ] `GET /api/v1/tests` — when called by a User-role user, results filtered to tests whose `category_id` is in the user's `user_category_access` list; Admin/Editor see all tests unfiltered
- [ ] Admin endpoints on `/api/v1/users/{id}/category-access`:
  - `GET` — list categories the user has access to
  - `POST` — grant access to a category (`{ category_id }`)
  - `DELETE /{category_id}` — revoke access to a category
- [ ] Duplicate grant returns clear error (not 500)
- [ ] `POST /api/v1/tests/{id}/submit` (or submission endpoint) checks `has_assignment(user_id, test_id)` for User-role; raises 403 if no active assignment exists

## Technical Notes
- Detect "User role" by checking `has_permission(user, "tests::*")` or `has_permission(user, "*::*")` to identify Admin/Editor vs User (skip filter if elevated)
- Alternatively compare `user.role.name` after eager-loading role, but prefer permission-based check for flexibility
- Submission assignment check: reuse `UserTestAssignment` model — query `WHERE user_id=... AND test_id=... AND (expires_at IS NULL OR expires_at > now())`
- Affected files:
  - `app/models/user_category_access.py` — new model
  - `app/models/__init__.py` — register new model
  - `app/api/v1/test.py` — update `GET /tests` filter logic
  - `app/api/v1/user.py` — add category-access sub-routes
  - `app/services/user_service.py` or new `app/services/category_access_service.py`
  - `app/repository/` — new or updated repo for category access queries
  - `app/api/v1/submission.py` (or equivalent) — add assignment guard
  - `alembic/versions/` — new migration
