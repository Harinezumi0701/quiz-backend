---
id: BE-009
title: Test Assignments — Assign tests to users
spec: spec/04-test-taking.md#test-assignments
status: done
priority: medium
---

## Context
Admins control which tests are available to which users, with optional expiry dates.

## Acceptance Criteria
- [x] `GET /test-assignments/` — list all assignments (filterable by user/test)
- [x] `POST /test-assignments/` — assign one test to one user
- [x] `POST /test-assignments/bulk` — assign one test to many users
- [x] `DELETE /test-assignments/{id}` — remove assignment
- [x] Duplicate assignment returns clear error (not 500)
- [x] `expires_at` respected when listing available tests for user

## Technical Notes
- Unique constraint on `(user_id, test_id)` in DB
- `app/api/v1/test_assignments.py`
