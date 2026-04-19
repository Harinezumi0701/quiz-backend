# Development & Installation Guide

## Prerequisites

- Python 3.12
- PostgreSQL
- Poetry (recommended) or pip
- Docker (optional)

## Setup

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Install dependencies
poetry install
# or
pip install -r requirements.txt

# 3. Apply database migrations
alembic upgrade head

# 4. Start the server
python run_debug.py   # development (hot reload, port 8008)
python run.py         # production (port 8000)
```

## Docker (quickest start)

```bash
# Start API + PostgreSQL
docker compose -f ci/docker/docker-compose.app.yml up

# API runs on port 8000, PostgreSQL on 5432
```

## Environment Variables (`.env`)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/quiz_db
DEBUG=true
SECRET_KEY=your-secret-key
S3_BUCKET_NAME=harinezumi-quiz-web
S3_REGION=ap-southeast-1
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
CLOUDFRONT_DOMAIN=...
```

## Server Commands

```bash
# Development with hot reload
python run_debug.py

# Production
python run.py

# Direct uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8008
```

## Important Notes

- `redirect_slashes=False` — trailing slashes do NOT redirect automatically
- `DEBUG=true` enables SQLAlchemy query echo
- `user_id` field is editable and alphanumeric (`[A-Za-z0-9._-]`), separate from the immutable UUID `id`
