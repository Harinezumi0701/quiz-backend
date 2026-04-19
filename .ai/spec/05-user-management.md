# Spec 05 — User Management

## Admin: User CRUD

- Endpoints: `GET /users/`, `POST /users/`, `GET /users/{id}`, `PUT /users/{id}`, `DELETE /users/{id}`
- `{id}` accepts either the UUID `id` or the editable `user_id` string
- Admin can change password: `PUT /users/{id}/change-password`
- Admin can assign role: `PUT /users/{id}/roles`

### User Fields

| Field | Rules |
|-------|-------|
| `user_id` | Unique, alphanumeric + `.`, `_`, `-`; editable by admin |
| `email` | Unique, valid email format |
| `full_name` | Non-empty string |
| `password` | Min 8 chars; hashed with bcrypt |
| `role_id` | Must reference existing role |
| `phone` | Optional |
| `birthday` | Optional date |
| `address` | Optional |
| `job_title` | Optional |
| `company` | Optional |
| `join_date` | Optional date |

### Acceptance Criteria

- [ ] Admin list supports pagination, text search, and filter by role
- [ ] Creating a user assigns the specified role (or default role if omitted)
- [ ] Deleting a user is a soft delete (`deleted_at` set)
- [ ] Admin cannot delete themselves
- [ ] `user_id` changes are validated for uniqueness

---

## Self-Service: Profile (`/me/`)

- `GET /me/` — returns current user's profile
- `PUT /me/` — updates own profile fields (not role, not user_id)
- `PUT /me/password` — change own password (requires current password)

### Acceptance Criteria

- [ ] User can update name, email, phone, birthday, address, job_title, company
- [ ] Password change requires correct current password; returns 400 if wrong
- [ ] User cannot change their own role or user_id via `/me/`
