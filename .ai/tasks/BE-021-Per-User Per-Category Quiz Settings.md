# Plan: Per-User Per-Category Quiz Settings

## Context
Currently the app has no per-user configuration. The `Test` model has a global `time_limit` field, but users cannot customize how many questions they want per day or how long they want per session for a given category. The requirement is: each user can set, per category, their own `questions_per_day` and `time_limit` (e.g., User A wants 20 questions/30 min for SAA, User B wants 60 questions/120 min for SAA).

---

## Database Change

**New table:** `user_category_settings`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | `server_default=uuidv7()` |
| `user_id` | UUID FK → users(id) | `ondelete=CASCADE`, indexed |
| `category_id` | UUID FK → categories(id) | `ondelete=CASCADE`, indexed |
| `questions_per_day` | Integer | `NOT NULL`, `server_default=20` |
| `time_limit` | Integer (minutes) | `NOT NULL`, `server_default=60` |
| `created_at` | TIMESTAMP | `server_default=now()` |
| `updated_at` | TIMESTAMP | `server_default=now()`, `onupdate` |

**Unique constraint:** `(user_id, category_id)` — one row per user per category.

No soft-delete — hard-delete is correct for settings rows.

---

## Files to Create

### 1. `app/models/user_category_settings.py`
SQLAlchemy model following the exact pattern of `categories.py` — UUID PK with `uuidv7()`, timestamps, relationships.
- `user = relationship("User", back_populates="category_settings")`
- `category = relationship("Category", back_populates="user_settings")`
- `UniqueConstraint("user_id", "category_id", name="uq_user_category_settings")`

### 2. `app/schemas/user_category_settings.py`
Pydantic v2 schemas:
- `UserCategorySettingsOut` — response shape (includes `category_name` from joined relationship)
- `UserCategorySettingsUpsertRequest` — `questions_per_day: int = Field(ge=1)`, `time_limit: int = Field(ge=1)`
- `UserCategorySettingsResponse` and `UserCategorySettingsListResponse` wrapping `SuccessResponse[T]`

### 3. `app/repository/user_category_settings_repo.py`
Sync SQLAlchemy Session, returns plain dicts (matches all other repos). Functions:
- `get_by_user_and_category(db, user_id, category_id) -> Optional[dict]`
- `list_by_user(db, user_id) -> List[dict]`
- `upsert(db, user_id, category_id, questions_per_day, time_limit) -> dict` — fetch-then-update or insert
- `delete_by_user_and_category(db, user_id, category_id) -> bool`

### 4. `app/services/user_category_settings_service.py`
Validates category exists (query `Category` with `deleted_at IS NULL`), raises `HTTPException(404)` for not-found cases, delegates to repo. Functions: `list_settings`, `get_setting`, `upsert_setting`, `delete_setting`.

### 5. `alembic/versions/w3x4y5z6a7_add_user_category_settings_table.py`
- `down_revision = 'v2w3x4y5z6'` (current head: `v2w3x4y5z6_add_default_column_to_roles.py`)
- `upgrade()`: `op.create_table(...)` + 3 indexes
- `downgrade()`: drop indexes + `op.drop_table(...)`

---

## Files to Modify

### `app/models/__init__.py`
Add: `from .user_category_settings import UserCategorySettings`

### `app/models/users.py`
Add to `User` model:
```python
category_settings = relationship("UserCategorySettings", back_populates="user", cascade="all, delete-orphan")
```

### `app/models/categories.py`
Add to `Category` model:
```python
user_settings = relationship("UserCategorySettings", back_populates="category", cascade="all, delete-orphan")
```

### `app/api/v1/me.py`
Add imports (`UUID` from `uuid`, schemas, service) and 4 new endpoints:
- `GET /me/settings/categories` — list all settings for current user
- `GET /me/settings/categories/{category_id}` — get setting for one category
- `PUT /me/settings/categories/{category_id}` — create or update (upsert)
- `DELETE /me/settings/categories/{category_id}` — delete setting

All use `Depends(get_current_user)` and `Depends(get_db)` — no special permissions needed.

---

## API Contract

```
GET    /api/v1/me/settings/categories
PUT    /api/v1/me/settings/categories/{category_id}
       Body: { "questions_per_day": 20, "time_limit": 30 }
GET    /api/v1/me/settings/categories/{category_id}
DELETE /api/v1/me/settings/categories/{category_id}
```

---

## Execution Order

1. Create model file → modify `__init__.py`, `users.py`, `categories.py`
2. Create schema file
3. Create repository file
4. Create service file
5. Create migration file
6. Add endpoints to `me.py`
7. Run `alembic upgrade head`

---

## Verification

1. `alembic upgrade head` — migration runs cleanly
2. `GET /api/v1/me/settings/categories` returns empty list for new user
3. `PUT /api/v1/me/settings/categories/{saa_category_id}` with `{"questions_per_day": 20, "time_limit": 30}` — creates row
4. Same PUT again with different values — updates row (upsert)
5. `GET /api/v1/me/settings/categories/{saa_category_id}` returns updated values
6. Repeat with second user — confirms per-user isolation (User B's settings don't affect User A's)
7. `DELETE /api/v1/me/settings/categories/{saa_category_id}` — returns 200, subsequent GET returns 404
8. `PUT` with `questions_per_day=0` — returns 422 validation error
