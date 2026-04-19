---
id: BE-004
title: User Management — Admin CRUD
spec: spec/05-user-management.md#admin-user-crud
status: done
priority: high
---

## Context
Admins need to create, update, and deactivate user accounts, and assign roles.

## Acceptance Criteria
- [x] `GET /users/` — paginated list with text search and role filter
- [x] `POST /users/` — create user with specified or default role
- [x] `GET /users/{id}` — lookup by UUID or `user_id` string
- [x] `PUT /users/{id}` — update profile fields
- [x] `DELETE /users/{id}` — soft delete (`deleted_at`)
- [x] `PUT /users/{id}/change-password` — admin sets new password
- [x] `PUT /users/{id}/roles` — assign role to user

## Technical Notes
- `app/api/v1/user.py`, `app/services/user_service.py`
- Lookup by UUID or user_id: try UUID parse first, fall back to user_id query
