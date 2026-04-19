---
id: BE-002
title: Auth — Token refresh & revoke
spec: spec/02-auth-rbac.md#authentication
status: done
priority: high
---

## Context
Refresh token rotation keeps sessions alive without re-login. Revoke enables secure logout.

## Acceptance Criteria
- [x] `POST /auth/token/refresh` returns new access + refresh tokens; old refresh token rejected after use
- [x] `POST /auth/token/revoke` marks refresh token as invalid in DB
- [x] Expired or invalid refresh tokens return 401

## Technical Notes
- Refresh tokens stored in `refresh_tokens` table with `expires_at`
- Rotation: delete old token, insert new on each refresh
