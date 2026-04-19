---
id: BE-007
title: Content — Test management
spec: spec/03-content-management.md#tests
status: done
priority: high
---

## Context
Tests are the core content unit. Admins create tests, assign them to users, and users take them.

## Acceptance Criteria
- [x] CRUD `/tests/`
- [x] Filter by category and text search
- [x] `time_limit` nullable (null = untimed)
- [x] `POST /tests/{id}/submit` — submit answers, returns scored result

## Technical Notes
- `app/api/v1/test.py`, `app/services/test_service.py`
- Submission scoring logic lives in service layer
