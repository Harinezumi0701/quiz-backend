---
id: BE-003
title: RBAC — Roles and permissions CRUD
spec: spec/02-auth-rbac.md#role--permission-model
status: done
priority: high
---

## Context
Dynamic role/permission system. Admins define roles and attach granular `namespace::action` permissions.

## Acceptance Criteria
- [x] CRUD `/roles/` — create, list, get, update, delete roles
- [x] `POST /roles/{id}/permissions` — attach permission to role
- [x] `DELETE /roles/{id}/permissions` — remove permission from role
- [x] CRUD `/permissions/` — manage standalone permissions
- [x] CRUD `/namespaces/` — manage namespaces (GET list is public, no auth)
- [x] Wildcard permissions (`*::*`, `ns::*`, `*::action`) evaluated correctly

## Technical Notes
- Permission check utility: `app/utils/permission_utils.py`
- `app/api/dependencies/permissions.py` for route-level enforcement
