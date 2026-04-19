---
id: BE-001
title: Auth — Register & Login endpoints
spec: spec/02-auth-rbac.md#authentication
status: done
priority: high
---

## Context
Core auth flow. Users need to register and log in to receive JWT tokens for all other API calls.

## Acceptance Criteria
- [x] `POST /auth/register` creates user with default role, returns access + refresh tokens
- [x] `POST /auth/login` returns tokens on valid credentials, 401 on invalid
- [x] Passwords hashed with bcrypt; plaintext never stored
- [x] `user_id` uniqueness validated on register

## Technical Notes
- `app/api/v1/auth.py`, `app/services/auth_service.py`
- Default role: query `roles` table for `default=True`
- Token generation: `app/utils/security.py`
