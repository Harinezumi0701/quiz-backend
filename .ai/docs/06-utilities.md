# Toolkits & Utilities

## Response Helpers (`app/utils/response.py`)

| Function | Purpose |
|----------|---------|
| `success_response()` | Creates `{ data, meta }` standardized success response |
| `error_response()` | Creates `{ error: { code, message, trace_id, details } }` response |

Always use these helpers in route handlers — never construct response dicts manually.

## Security (`app/utils/security.py`)

| Function | Purpose |
|----------|---------|
| `create_access_token()` | Encode JWT (30 min expiry) |
| `decode_access_token()` | Validate and decode JWT |
| `hash_password()` | bcrypt password hashing |
| `verify_password()` | bcrypt password verification |
| `generate_refresh_token()` | Generate opaque refresh token |

## Permission Utils (`app/utils/permission_utils.py`)

| Function | Purpose |
|----------|---------|
| `build_permission_string()` | Construct `namespace::action` string |
| `method_to_action()` | Map HTTP method → action (`GET→read`, etc.) |

## Search & Pagination (`app/utils/search_pagination.py`)

| Function | Purpose |
|----------|---------|
| `paginate_query_with_multiple_filters()` | Apply search, filters, and pagination to a SQLAlchemy query |
| `get_pagination_meta()` | Build `meta` block with `total`, `page`, `per_page`, `total_pages` |

All list endpoints use these for consistent pagination behavior (max 100 per page).

## Error Utils (`app/utils/error_utils.py`)

Maps error codes to user-facing messages. Use constants from `app/constants/error_codes.py` and `app/constants/error_messages.py`.

## Datetime Utils (`app/utils/datetime_utils.py`)

| Function | Purpose |
|----------|---------|
| UTC normalization | Ensure all datetimes stored/compared as UTC |
| Timestamp conversion | Convert between datetime and Unix timestamps |

## Constants (`app/constants/`)

| File | Contents |
|------|---------|
| `api_paths.py` | API route prefix constants |
| `app_config.py` | App-wide configuration values |
| `cors.py` | CORS allowed origins/methods |
| `security.py` | JWT secret, algorithm, token expiry |
| `error_codes.py` | Error code string constants |
| `error_messages.py` | User-facing error message strings |
| `permissions.py` | Permission string constants |

Import via: `from app.constants import CONSTANT_NAME`
