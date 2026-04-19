# Spec 02 — Authentication & RBAC

## Authentication

### Registration

- Fields: `email`, `password`, `full_name`, `user_id` (optional, auto-generated if omitted)
- `user_id` must match `[A-Za-z0-9._-]`; unique across users
- Returns: access token + refresh token on success
- Default role assigned from the role marked `default: true` in the roles table

### Login

- Fields: `email`, `password`
- Returns: access token (short-lived JWT) + refresh token (long-lived, stored in DB)
- Failed login: `401 INVALID_CREDENTIALS`

### Token Refresh

- `POST /auth/token/refresh` with refresh token in body
- Returns new access token + new refresh token (rotation)
- Old refresh token is revoked (one-time use)

### Logout / Revoke

- `POST /auth/token/revoke` invalidates the provided refresh token
- Access tokens are stateless and expire naturally

---

## Role & Permission Model

### Roles

- Stored in `roles` table: `id`, `name`, `description`, `default` (bool)
- One role can be marked `default: true` — assigned to new registrations
- Admins can create/update/delete roles
- Admins can assign a role to a user via `PUT /users/{id}/roles`

### Permissions

- Format: `namespace::action`
- Actions map to HTTP methods: `read` (GET), `create` (POST), `update` (PUT), `delete` (DELETE)
- Wildcards: `*::*` (superadmin), `namespace::*`, `*::action`
- Permissions are attached to roles via `role_permissions` table
- Namespaces are managed via `/namespaces/` (list is public, no auth)

### Permission Check Flow

1. Extract JWT → get `user_id`
2. Load user → get `role_id`
3. Load `role_permissions` for role
4. Check if any permission matches `namespace::action` (with wildcard expansion)
5. Deny with `403 FORBIDDEN` if no match

---

## Acceptance Criteria

- [ ] Register creates user with default role and returns tokens
- [ ] Login returns tokens on valid credentials, 401 on invalid
- [ ] Refresh rotates tokens (old token rejected after refresh)
- [ ] Revoke invalidates refresh token
- [ ] Protected endpoints reject requests without valid Bearer token
- [ ] Permission check denies users without required `namespace::action`
- [ ] Wildcard permissions (`*::*`) grant access to everything
