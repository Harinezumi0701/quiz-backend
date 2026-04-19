# Project Overview & Structure

## Summary

A FastAPI-based quiz management backend with role-based access control, JWT authentication, AWS S3 file storage, and PostgreSQL database.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.120.4 |
| Runtime | Python 3.12 |
| ASGI Server | Uvicorn 0.38.0 |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL (psycopg2 2.9.11) |
| Migrations | Alembic 1.17.1 |
| Auth | python-jose (JWT) + passlib/bcrypt |
| Storage | AWS S3 via boto3 + CloudFront CDN |
| Dependency Mgmt | Poetry |

## Project Structure

```
quiz-backend/
├── app/
│   ├── api/v1/             # Route handlers (auth, user, me, question, category, test, answer, role, permission, namespace, upload, user_tests, test_assignments)
│   ├── api/dependencies/   # FastAPI dependencies (auth, permissions)
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── services/           # Business logic layer
│   ├── repository/         # Database access layer
│   ├── constants/          # App-wide constants (api_paths, app_config, cors, security, error_codes, error_messages, permissions)
│   ├── utils/              # Helpers (security, response, permission_utils, search_pagination, error_utils, datetime_utils)
│   ├── middleware/         # ResponseWrapperMiddleware + exception handlers
│   ├── db/                 # Database session configuration
│   └── main.py             # FastAPI app entry point
├── alembic/                # Migration files
├── ci/docker/              # Dockerfile + docker-compose.app.yml
├── scripts/                # Utility scripts
├── tests/                  # Test files
├── run.py                  # Production server entry
├── run_debug.py            # Debug server entry (hot reload, port 8008)
├── pyproject.toml          # Poetry config
└── requirements.txt        # Pip requirements
```

## Notable Design Decisions

- Users have two IDs: immutable UUID `id` and editable unique `user_id` string (supports lookup by either)
- All list endpoints support pagination (max 100 per page) with text search and multiple filter conditions
- Bulk operations supported for test assignments and answer submissions
- Constants are fully centralized under `app/constants/` — avoid hardcoding values elsewhere
