---
id: BE-005
title: Me — Profile & password self-service
spec: spec/05-user-management.md#self-service-profile-me
status: done
priority: high
---

## Context
Authenticated users manage their own profile and change their password without admin involvement.

## Acceptance Criteria
- [x] `GET /me/` — returns own profile
- [x] `PUT /me/` — updates allowed fields (no role or user_id change)
- [x] `PUT /me/password` — requires correct current password; returns 400 if wrong

## Technical Notes
- `app/api/v1/me.py`
- Verify current password before hashing and saving new password
