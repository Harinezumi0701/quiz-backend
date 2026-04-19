# API Catalog & Permissions

All endpoints are under `/api/v1/`.

API docs available at:
- Swagger UI: `http://localhost:8008/docs`
- ReDoc: `http://localhost:8008/redoc`

## Endpoint Summary

| Resource | Endpoints |
|----------|-----------|
| Auth | POST /auth/register, /auth/login, /auth/token/refresh, /auth/token/revoke |
| Users | CRUD /users/, GET/PUT/DELETE /users/{id}, PUT /users/{id}/change-password, PUT /users/{id}/roles |
| Me | GET/PUT /me/, GET /me/dashboard, PUT /me/password |
| Questions | CRUD /questions/, GET /questions/{id} |
| Categories | CRUD /categories/, GET /categories/{id}/questions |
| Tests | CRUD /tests/, POST /tests/{id}/submit |
| Answers | CRUD /answers/ |
| Roles | CRUD /roles/, POST/DELETE /roles/{id}/permissions |
| Permissions | CRUD /permissions/ |
| Namespaces | CRUD /namespaces/ (GET list is public, no auth required) |
| Uploads | POST /uploads/ (returns S3 presigned URL) |
| User Tests | GET /user-tests/, GET /user-tests/{test_id}/questions |
| Test Assignments | GET/POST /test-assignments/, POST /test-assignments/bulk, DELETE /test-assignments/{id} |
| Health | GET /api/v1/health |

## Permission System

Permission format: `namespace::action`

| HTTP Method | Action |
|-------------|--------|
| GET | read |
| POST | create |
| PUT | update |
| DELETE | delete |

Wildcards: `*::*` (all), `namespace::*` (all actions in namespace), `*::action` (action across all namespaces)

## Notable Behaviors

- Dashboard endpoint (`GET /me/dashboard`) provides accuracy stats overall, by-category, by-test, and recent activity
- AWS S3 presigned URLs used for direct browser-to-S3 uploads; CloudFront CDN for public read access
- Bulk operations supported for test assignments and answer submissions
- All list endpoints support pagination (max 100 per page) with text search and multiple filter conditions
