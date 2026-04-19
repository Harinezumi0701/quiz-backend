# Architecture & Data Flow

## Layered Architecture (Request Flow)

```
HTTP Request
  → CORS Middleware
  → ResponseWrapperMiddleware
  → Route Handler (api/v1/)
    → Service Layer (services/)
      → Repository Layer (repository/)
        → SQLAlchemy ORM (models/)
  → ResponseWrapperMiddleware wraps response
← HTTP Response
```

### Layer Responsibilities

| Layer | Location | Responsibility |
|-------|----------|---------------|
| API | `app/api/v1/` | Route definitions, input validation via Pydantic, calls service layer |
| Service | `app/services/` | Business logic, orchestration, raises HTTPException for rule violations |
| Repository | `app/repository/` | Direct DB operations via SQLAlchemy ORM, no business logic |
| Models | `app/models/` | SQLAlchemy ORM table definitions and relationships |
| Schemas | `app/schemas/` | Pydantic models for request/response validation |

## Response Format

**Success:**
```json
{ "data": { ... }, "meta": { ... } }
```

**Error:**
```json
{ "error": { "code": "ERROR_CODE", "message": "...", "trace_id": "uuid", "details": null } }
```

The `ResponseWrapperMiddleware` automatically wraps all 2xx responses. API handlers should use `success_response()` and `error_response()` helpers — never manually construct response structures.

## Authentication Flow

1. `POST /api/v1/auth/register` or `/auth/login` → returns JWT access token (30 min) + optional refresh token (7 days, if `remember_me=true`)
2. Protected endpoints require `Authorization: Bearer <token>` header
3. `get_current_user` dependency (in `app/api/dependencies/auth.py`) validates JWT and loads user from DB
4. Refresh via `POST /api/v1/auth/token/refresh`

## RBAC Permission System

- Users are assigned a Role; roles have multiple RolePermissions
- Permission format: `namespace::action` (e.g., `categories::read`)
- Wildcards supported: `*::*`, `namespace::*`, `*::action`
- HTTP method → action mapping: `GET→read`, `POST→create`, `PUT→update`, `DELETE→delete`
- Default permissions applied if user has no role
- Permission check via `@require_namespace_permission(namespace, method)` dependency
