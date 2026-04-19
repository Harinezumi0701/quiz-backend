# Backend CI/CD Task Breakdown

**Project**: Quiz Platform — Backend (FastAPI + Python 3.12 + SQLAlchemy + Alembic + PostgreSQL)
**Created**: 2026-03-30
**Owner**: Backend Team
**Context**: No CI/CD pipeline exists. This task set establishes a complete GitHub Actions CI/CD pipeline for the backend service.

---

## Task Index

| ID | Title | Priority | Depends On |
|---|---|---|---|
| TASK-BE-CI-01 | Add ruff (linter) to pyproject.toml dev dependencies | High | — |
| TASK-BE-CI-02 | Add pytest and testing dependencies to pyproject.toml | High | — |
| TASK-BE-CI-03 | Write minimal pytest smoke tests (startup + health endpoint) | High | 02, 09 |
| TASK-BE-CI-04 | Add explicit CMD instruction to production Dockerfile | High | — |
| TASK-BE-CI-05 | Add `.dockerignore` to reduce Docker build context | Medium | — |
| TASK-BE-CI-06 | Document and integrate Alembic migration step into CD deploy | High | — |
| TASK-BE-CI-07 | Create CI GitHub Actions workflow (`ci-be.yml`) | High | 01, 02, 03, 04, 05 |
| TASK-BE-CI-08 | Create CD GitHub Actions workflow (`cd-be.yml`) | High | 07 |
| TASK-BE-CI-09 | Add `GET /health` endpoint to FastAPI application | High | — |

---

## TASK-BE-CI-01 — Add ruff (Linter) to pyproject.toml Dev Dependencies

### Description

No linting tooling exists in the backend. `ruff` is a fast, all-in-one Python linter and formatter that replaces `flake8`, `isort`, and `pyupgrade`. It integrates natively with Poetry and runs in milliseconds even on large codebases.

### Services/Modules Affected

- `pyproject.toml` — add `ruff` to `[tool.poetry.group.dev.dependencies]`
- `ruff.toml` or `[tool.ruff]` section in `pyproject.toml` — ruff configuration

### Database Impact

None.

### API Changes

None.

### Implementation Steps

1. Add `ruff` to pyproject.toml dev group:
   ```toml
   [tool.poetry.group.dev.dependencies]
   ruff = "^0.4.0"
   ```

2. Add `[tool.ruff]` configuration in `pyproject.toml`:
   ```toml
   [tool.ruff]
   line-length = 100
   target-version = "py312"

   [tool.ruff.lint]
   select = ["E", "F", "I", "UP", "B", "SIM"]
   ignore = ["E501"]  # Line length handled by formatter

   [tool.ruff.lint.per-file-ignores]
   "tests/*" = ["S101"]  # Allow assert in tests
   ```

3. Add lint scripts to Makefile or document as direct commands:
   ```
   poetry run ruff check .          # lint
   poetry run ruff check . --fix    # auto-fix
   poetry run ruff format .         # format (replaces black)
   ```

4. Run `ruff check .` and fix all violations (or disable specific rules per-file if intentional).

5. Run `ruff format .` to enforce consistent formatting. Commit formatted output.

### Acceptance Criteria

- `poetry run ruff check .` exits with code `0` on the clean codebase
- `poetry run ruff check .` exits with code `1` when violations exist
- Ruff config is committed to `pyproject.toml` (no separate config file needed)
- All existing code passes linting before CI is enabled

### Test Cases

- Introduce unused import → ruff fails with `F401`
- Introduce unsorted imports → ruff fails with `I001`
- Clean codebase → ruff passes
- `ruff check . --fix` → auto-fixable issues resolved, no manual editing required

---

## TASK-BE-CI-02 — Add pytest and Testing Dependencies to pyproject.toml

### Description

No test infrastructure exists. This task installs pytest and related dependencies required for running automated tests against the FastAPI application.

### Services/Modules Affected

- `pyproject.toml` — add dev dependencies
- `tests/` directory (new) — test files will be created in TASK-BE-CI-03

### Database Impact

None (dependency installation only).

### API Changes

None.

### Implementation Steps

1. Add the following to `[tool.poetry.group.dev.dependencies]`:
   ```toml
   [tool.poetry.group.dev.dependencies]
   ruff = "^0.4.0"
   pytest = "^8.0.0"
   pytest-asyncio = "^0.23.0"
   httpx = "^0.27.0"       # For FastAPI TestClient (async-compatible)
   pytest-cov = "^5.0.0"   # Coverage reporting
   ```

2. Add `[tool.pytest.ini_options]` to `pyproject.toml`:
   ```toml
   [tool.pytest.ini_options]
   asyncio_mode = "auto"
   testpaths = ["tests"]
   python_files = ["test_*.py"]
   python_functions = ["test_*"]
   addopts = "-v --tb=short"
   ```

3. Create `tests/` directory:
   ```
   tests/
   ├── __init__.py
   └── conftest.py
   ```

4. In `tests/conftest.py`, define the shared test fixtures:
   ```python
   import pytest
   from httpx import AsyncClient, ASGITransport
   from app.main import app

   @pytest.fixture
   async def client():
       async with AsyncClient(
           transport=ASGITransport(app=app),
           base_url="http://test"
       ) as ac:
           yield ac
   ```

5. Run `poetry install --with dev` to verify all deps resolve without conflict.

### Acceptance Criteria

- `poetry run pytest tests/ -v` completes without import errors
- `httpx.AsyncClient` can connect to the FastAPI app via `ASGITransport` (no running server needed)
- `pytest-asyncio` is configured for auto mode (no `@pytest.mark.asyncio` needed per test)
- `poetry install --with dev` resolves without version conflicts

### Test Cases

- `poetry run pytest tests/ --collect-only` → test collection succeeds (even with 0 tests)
- `poetry run pytest --version` → returns installed version
- Import `from app.main import app` inside a test succeeds

---

## TASK-BE-CI-03 — Write Minimal pytest Smoke Tests (Startup + Health Endpoint)

### Description

With testing infrastructure in place (TASK-BE-CI-02) and the health endpoint created (TASK-BE-CI-09), this task writes the initial smoke test suite to validate:
1. FastAPI application starts without error
2. `GET /health` returns 200 with expected payload
3. `GET /nonexistent` returns 404 (error handling works)

These tests serve as the CI gate — they block deployment of broken builds.

**Prerequisite**: TASK-BE-CI-09 (health endpoint) must be completed first.

### Services/Modules Affected

- `tests/test_health.py` (new)
- `tests/conftest.py` (updated with DB-related fixtures if needed)

### Database Impact

Tests use the `DATABASE_URL` environment variable. In CI, this points to a PostgreSQL service container (not production). Tests should not require a real database for smoke tests — use the app-level health check only.

### API Changes

None (test-only).

### Implementation Steps

1. Create `tests/test_health.py`:
   ```python
   import pytest

   async def test_health_returns_200(client):
       response = await client.get("/health")
       assert response.status_code == 200

   async def test_health_response_structure(client):
       response = await client.get("/health")
       data = response.json()
       assert "data" in data
       assert data["data"]["status"] == "ok"

   async def test_not_found_returns_404(client):
       response = await client.get("/nonexistent-path-xyz")
       assert response.status_code == 404

   async def test_health_database_field_present(client):
       response = await client.get("/health")
       data = response.json()
       assert "database" in data["data"]
   ```

2. Ensure `conftest.py` uses `ASGITransport` (no external server required):
   ```python
   # conftest.py already defined in TASK-BE-CI-02
   ```

3. Confirm `DATABASE_URL` is set in the test environment (either via `.env.test` or via CI environment variables).

4. Run tests locally:
   ```bash
   DATABASE_URL=postgresql+psycopg2://testuser:testpass@localhost:5432/test_db \
   SECRET_KEY=test-key \
   poetry run pytest tests/ -v
   ```

### Acceptance Criteria

- All 4 smoke tests pass with a running PostgreSQL instance
- Tests run in < 30 seconds
- `pytest-cov` reports ≥ 30% coverage on `app/api/` after smoke tests
- Tests do not leave any data in the database (no side effects)
- `DATABASE_URL` is read from environment, never hardcoded in tests

### Test Cases

- Stop PostgreSQL → tests that require DB fail gracefully (not with an unhandled exception)
- Change `/health` response format → `test_health_response_structure` fails with clear assertion message
- Run with `--cov=app --cov-report=term-missing` → coverage report generated

---

## TASK-BE-CI-04 — Add Explicit CMD Instruction to Production Dockerfile

### Description

The current `ci/docker/Dockerfile` has no `CMD` instruction. The `command:` directive in `docker-compose.app.yml` provides the startup command. This is acceptable for docker-compose usage, but:
1. It makes the image unusable standalone (e.g., `docker run quiz-be` does nothing)
2. CI validation of the Docker image cannot confirm the app starts correctly
3. It is a Docker best-practice violation

### Services/Modules Affected

- `ci/docker/Dockerfile` — add `CMD` instruction

### Database Impact

None.

### API Changes

None.

### Implementation Steps

1. Open `ci/docker/Dockerfile` and add at the end:
   ```dockerfile
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. The `command:` in `docker-compose.app.yml` can remain — it overrides `CMD` when needed (e.g., passing additional flags). The `CMD` serves as a safe default.

3. Rebuild the image locally and verify startup:
   ```bash
   docker build -f ci/docker/Dockerfile -t quiz-be:test .
   docker run --env-file .env -p 8000:8000 quiz-be:test
   # Should start uvicorn without errors
   ```

### Acceptance Criteria

- `docker run quiz-be:test` starts the FastAPI app without additional arguments
- Uvicorn binds to `0.0.0.0:8000`
- App starts within 10 seconds (no DB connection required for startup)
- `docker-compose.app.yml` behavior is unchanged (its `command:` overrides CMD)

### Test Cases

- `docker run -e DATABASE_URL=... -e SECRET_KEY=... quiz-be:test` → uvicorn starts, app responds on port 8000
- `docker run quiz-be:test --help` → uvicorn help displayed (CMD is overrideable)

---

## TASK-BE-CI-05 — Add `.dockerignore` to Reduce Docker Build Context

### Description

Without a `.dockerignore`, Docker includes the entire project directory in the build context: `.git/`, `__pycache__/`, `.venv/`, `tests/`, and other irrelevant files. This inflates the build context, slows CI, and risks including sensitive files in the image.

### Services/Modules Affected

- `.dockerignore` (new file, project root)

### Database Impact

None.

### API Changes

None.

### Implementation Steps

Create `.dockerignore` in the project root:

```dockerignore
# Python cache
__pycache__/
*.py[cod]
*$py.class
*.pyc
*.pyo

# Virtual environments
.venv/
venv/
env/

# Poetry
poetry.lock   # Keep in context for reproducible builds — remove this line

# Git
.git/
.gitignore
.gitattributes

# Tests (not needed in production image)
tests/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/

# IDE/editor files
.vscode/
.idea/
*.swp
*.swo

# Environment files
.env
.env.*
!.env.example

# OS files
.DS_Store
Thumbs.db

# Logs
*.log

# Alembic (migrations ARE needed — keep alembic/ and alembic.ini)
# Do NOT add alembic/ to dockerignore

# CI/docs
.ai/
task/
ci/*.md
```

> **Important**: Do NOT exclude `alembic/` or `alembic.ini` — migrations run inside the container.

### Acceptance Criteria

- `node_modules/`-equivalent (`.venv/`) excluded from context
- `.env` files excluded (never in image)
- `__pycache__/` excluded
- `tests/` excluded (reduces image attack surface)
- `alembic/` and `alembic.ini` remain accessible in the image
- Build context size < 20 MB

### Test Cases

- `docker build .` → observe build context size in output
- `docker run quiz-be:test sh -c "ls /app"` → no `.env`, no `tests/`, no `.git/` visible
- `docker run quiz-be:test sh -c "ls /app/alembic"` → alembic migrations present

---

## TASK-BE-CI-06 — Document and Integrate Alembic Migration Step into CD Deploy

### Description

Alembic is installed and configured but no migration execution step exists in any deployment process. Without this, schema changes pushed via CD will break the application at runtime (table not found, column missing, etc.).

The CD workflow must run `alembic upgrade head` after the new container starts and before traffic is served.

### Services/Modules Affected

- `alembic.ini` — verify `script_location` and `sqlalchemy.url` configuration
- `alembic/env.py` — verify it reads `DATABASE_URL` from environment
- `.github/workflows/cd-be.yml` — migration step added in TASK-BE-CI-08

### Database Impact

- **Direct impact**: `alembic upgrade head` applies all pending migrations
- **Risk**: Irreversible if migration drops columns or tables
- **Mitigation**: Always test migrations locally before merging to `production`

### API Changes

None.

### Implementation Steps

1. Verify `alembic/env.py` reads the database URL from the environment:
   ```python
   import os
   from sqlalchemy import engine_from_config

   # Ensure this pattern or equivalent exists:
   config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
   ```

2. Verify `alembic.ini` `script_location` points to `alembic/`:
   ```ini
   script_location = alembic
   ```

3. Define migration execution command for CD (used in `cd-be.yml`):
   ```bash
   docker exec quiz_api_prod alembic upgrade head
   ```
   This runs inside the already-started container, using the container's `DATABASE_URL`.

4. Define rollback command (used in manual rollback only):
   ```bash
   docker exec quiz_api_prod alembic downgrade -1
   ```

5. Add a pre-deploy database backup command to the CD workflow as a safety gate:
   ```bash
   docker exec quiz_db_prod pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > \
     /home/deploy/quiz/be/backups/pre_deploy_$(date +%Y%m%d_%H%M%S).sql
   ```

6. Ensure `/home/deploy/quiz/be/backups/` directory exists on the server (manual one-time setup):
   ```bash
   mkdir -p /home/deploy/quiz/be/backups
   ```

### Acceptance Criteria

- `alembic upgrade head` runs successfully in CI test environment (against PostgreSQL service container)
- `alembic upgrade head` runs in CD workflow after container restart
- A database backup is taken before each production migration
- `alembic current` output is logged in CD workflow for audit trail
- `alembic downgrade -1` is documented and tested for rollback

### Test Cases

- Create a new migration with `alembic revision --autogenerate` → apply with `upgrade head` → verify schema
- Run `upgrade head` twice → idempotent (no error, "Running upgrade..." only once)
- Run `downgrade -1` after `upgrade head` → schema reverts correctly
- Deploy with invalid migration SQL → migration fails, container remains on old version

---

## TASK-BE-CI-07 — Create CI GitHub Actions Workflow (`ci-be.yml`)

### Description

Create the CI pipeline that runs on every push to `feature/**` branches. Provides fast feedback before merging to `production`.

### Services/Modules Affected

- `.github/workflows/ci-be.yml` (new file)

### Database Impact

CI uses a PostgreSQL 15 service container (ephemeral, test-only). No production database is touched.

### API Changes

None.

### Workflow Specification

**Trigger**: Push to `feature/**`
**Runner**: `ubuntu-latest`
**Services**: `postgres:15-alpine` with healthcheck

**Steps** (in order):
1. `actions/checkout@v4`
2. `actions/setup-python@v5` — Python 3.12
3. Install Poetry via curl script
4. `poetry install --with dev`
5. `poetry run ruff check .` — lint
6. `poetry run mypy app/ --ignore-missing-imports` — type check (non-blocking initially)
7. `poetry run pytest tests/ -v --tb=short` — run tests against PostgreSQL service container
8. Docker build validation (build only, no push)

**Full YAML**: See `CICD_Document.md` Section 9.

### Acceptance Criteria

- Workflow file is valid GitHub Actions YAML
- Workflow triggers on `feature/**` push only (not `production`)
- PostgreSQL service container is healthy before pytest runs
- `DATABASE_URL` and `SECRET_KEY` are injected as CI environment variables (test values, not production)
- Ruff lint failure blocks workflow
- Test failure blocks workflow
- Mypy failure is non-blocking initially (set `continue-on-error: true`)
- Total CI runtime < 5 minutes

### Test Cases

- Push with a ruff violation → CI fails at lint step, tests do not run
- Push with a failing test → CI fails at test step, Docker build does not run
- Push clean code → all steps pass
- Push to `production` → this workflow does NOT trigger

---

## TASK-BE-CI-08 — Create CD GitHub Actions Workflow (`cd-be.yml`)

### Description

Create the CD pipeline that triggers on every push to `production`. This pipeline runs lint + tests, builds the Docker image, pushes to GHCR, deploys to the on-prem server, runs Alembic migrations, and validates the deployment via health check.

### Services/Modules Affected

- `.github/workflows/cd-be.yml` (new file)

### Database Impact

- `alembic upgrade head` runs against the **production database** during deployment
- Database backup is taken before migration (see TASK-BE-CI-06)

### API Changes

None.

### Workflow Specification

**Trigger**: Push to `production`
**Runner**: `ubuntu-latest`
**Services**: `postgres:15-alpine` (for CI test gate only)

**Steps** (in order):
1. `actions/checkout@v4`
2. `actions/setup-python@v5` — Python 3.12
3. Install Poetry
4. `poetry install --with dev`
5. `poetry run ruff check .` — lint gate
6. `poetry run pytest tests/ -v` — test gate (against CI PostgreSQL service, not production)
7. `docker/login-action@v3` — GHCR login
8. `docker/metadata-action@v5` — generate tags: `<sha>`, `production`, `YYYYMMDD`
9. `docker/build-push-action@v5` — build and push with all tags, with registry cache
10. `appleboy/ssh-action@v1.0.3` — SSH deploy:
    - Backup database: `docker exec quiz_db_prod pg_dump ...`
    - `docker pull ghcr.io/<org>/quiz-be:production`
    - `docker compose up -d --no-deps api`
    - Wait 15 seconds for container to initialize
    - `docker exec quiz_api_prod alembic upgrade head`
    - Log: `docker exec quiz_api_prod alembic current`
    - Prune old images: `docker image prune -f --filter "until=720h"`
11. `appleboy/ssh-action@v1.0.3` — Health check:
    - Poll `http://localhost:8000/health` with 10 retries (5s interval)
    - Fail workflow if unhealthy

**Required GitHub Secrets**: `SSH_PRIVATE_KEY`, `SSH_HOST`, `SSH_USER`, `SSH_PORT`, `GHCR_TOKEN`

**Full YAML**: See `CICD_Document.md` Section 10.

### Acceptance Criteria

- Workflow triggers ONLY on `production` push
- Lint and test gates block deployment of broken code
- All 3 image tags appear in GHCR after successful run
- Alembic migration runs inside the production container (not in CI runner)
- Database backup is created before migration
- Health check passes before workflow is marked successful
- CD completes in < 20 minutes total
- Workflow failure leaves a clear error message identifying which step failed

### Test Cases

- Push to `production` → full pipeline runs, container restarts with new image
- Push to `feature/**` → this workflow does NOT trigger
- Lint failure → workflow stops at step 5, no deploy occurs
- Test failure → workflow stops at step 6, no deploy occurs
- Image push failure → SSH deploy step does not execute
- `alembic upgrade head` fails → workflow fails, old container remains running (health check validates this)
- Health check fails → workflow marked failed, human intervention required

---

## TASK-BE-CI-09 — Add `GET /health` Endpoint to FastAPI Application

### Description

No health check endpoint exists in the backend. The CD workflow requires a reliable HTTP endpoint to validate post-deployment health. The endpoint must check:
1. Application startup (framework is serving requests)
2. Database connectivity (SQLAlchemy can reach PostgreSQL)

### Services/Modules Affected

- `app/api/v1/health.py` (new file) — health check route
- `app/api/v1/__init__.py` or `app/main.py` — register the new router
- `app/api/v1/router.py` (if exists) — include health router

### Database Impact

The health endpoint executes a simple `SELECT 1` against the database to verify connectivity. This is a read-only operation with negligible impact.

### API Changes

**New endpoint**:

```
GET /health
```

**Response (200 OK)**:
```json
{
  "data": {
    "status": "ok",
    "database": "connected",
    "version": "1.0.0"
  }
}
```

**Response (503 Service Unavailable)** — if database is unreachable:
```json
{
  "data": {
    "status": "degraded",
    "database": "disconnected",
    "version": "1.0.0"
  }
}
```

Note: Returns `200` even in degraded state to allow liveness checks to pass. Returns `503` only when the application itself cannot respond.

### Validation Rules

- No authentication required (endpoint must be publicly accessible for health checks)
- No request body or query parameters
- Response always conforms to the standard `ApiSuccessResponse` wrapper format used by `ResponseWrapperMiddleware`
- Database check uses a try/except — if DB unreachable, returns `"database": "disconnected"` with HTTP 200 (not 500)

### Implementation Steps

1. Create `app/api/v1/health.py`:
   ```python
   from fastapi import APIRouter, Depends
   from sqlalchemy.orm import Session
   from sqlalchemy import text
   from app.db.session import get_db   # adjust import path to match actual session module

   router = APIRouter(prefix="/health", tags=["health"])

   APP_VERSION = "1.0.0"

   @router.get("")
   def health_check(db: Session = Depends(get_db)):
       db_status = "disconnected"
       try:
           db.execute(text("SELECT 1"))
           db_status = "connected"
       except Exception:
           pass
       return {
           "status": "ok",
           "database": db_status,
           "version": APP_VERSION,
       }
   ```

2. Register the router in the main app or router file. Confirm the final URL is `GET /health` (not `/api/v1/health`).

3. Exclude the `/health` endpoint from RBAC permission checks (it must be unauthenticated).

4. Verify `ResponseWrapperMiddleware` wraps the response correctly (output should be `{"data": {...}}`).

### Acceptance Criteria

- `GET /health` returns HTTP 200 with correct JSON structure
- Response contains `status`, `database`, and `version` fields
- `database: "connected"` only when SQLAlchemy can execute `SELECT 1`
- `database: "disconnected"` when PostgreSQL is unreachable (does not crash the endpoint)
- Endpoint requires no authentication token
- Endpoint is excluded from RBAC middleware
- Response is wrapped in `{"data": {...}}` by `ResponseWrapperMiddleware`

### Test Cases

- `GET /health` with running PostgreSQL → `{"data": {"status": "ok", "database": "connected", "version": "1.0.0"}}`
- `GET /health` with PostgreSQL stopped → `{"data": {"status": "ok", "database": "disconnected", "version": "1.0.0"}}` (HTTP 200)
- `GET /health` with a valid JWT in headers → still works (auth not required)
- `GET /health` with no headers → works (no 401)
- Test `test_health_returns_200` in `tests/test_health.py` passes (TASK-BE-CI-03)
