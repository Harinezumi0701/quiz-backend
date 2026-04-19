# BE-020 — Email Account Activation (AWS SES)

**Status:** TODO
**Layer:** Backend
**Risk Level:** High

---

## 1. Root Cause Analysis

### Context
Newly registered users can currently access the application immediately. A secure email-based activation flow must be implemented:
- On registration, account is created with `is_active = False`
- An activation email is sent via **AWS SES (boto3)**
- User must click the activation link within 2 hours
- Inactive users are rejected with `403 Forbidden` on all authenticated endpoints

### Affected Modules
- `app/models/users.py`
- `app/services/auth_service.py`
- `app/repository/auth_repo.py`
- `app/api/v1/auth.py`
- `app/api/dependencies/auth.py`
- `app/utils/email_service.py` (new)
- `alembic/versions/` (new migration)

---

## 2. Task Breakdown

---

### Task BE-020-A: Database Migration — Add Activation Fields to `users`

**Title:** Add `is_active`, `activation_token`, `activation_expires_at` to `users` table

**Migration File:** new file in `alembic/versions/`

**Upgrade Logic:**
```sql
ALTER TABLE users
  ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT FALSE,
  ADD COLUMN activation_token VARCHAR(255) DEFAULT NULL,
  ADD COLUMN activation_expires_at TIMESTAMP DEFAULT NULL;

-- Backfill existing users to avoid locking out current accounts
UPDATE users SET is_active = TRUE WHERE deleted_at IS NULL;
```

**Downgrade Logic:**
```sql
ALTER TABLE users
  DROP COLUMN is_active,
  DROP COLUMN activation_token,
  DROP COLUMN activation_expires_at;
```

**Database Impact:**
- Existing users: backfilled to `is_active = TRUE` (preserve access)
- New users: default `is_active = FALSE`

**Validation Rules:**
- `is_active` must be NOT NULL with default `FALSE`
- `activation_token` and `activation_expires_at` must be nullable

**Acceptance Criteria:**
- `alembic upgrade head` → `\d users` shows 3 new columns
- All pre-existing users have `is_active = TRUE`
- `alembic downgrade -1` removes the 3 columns cleanly

**Required Tests:**
- Verify upgrade/downgrade cycle in local dev database

---

### Task BE-020-B: Update `User` ORM Model

**Title:** Add activation fields to `User` SQLAlchemy model

**Files Affected:**
- `app/models/users.py`

**Changes:**
```python
is_active = Column(Boolean, nullable=False, default=False)
activation_token = Column(String(255), nullable=True, default=None)
activation_expires_at = Column(TIMESTAMP(timezone=True), nullable=True, default=None)
```

**Database Impact:** None (migration in BE-020-A)

**Acceptance Criteria:**
- ORM model reflects new columns
- Application starts without import errors

---

### Task BE-020-C: Implement AWS SES Email Service

**Title:** Create `app/utils/email_service.py` using boto3 + AWS SES

**Description:**
Implement an email service that sends transactional emails via AWS SES using the boto3 SDK. Credentials must be loaded from environment variables only — never hardcoded.

**File to Create:** `app/utils/email_service.py`

**Dependency to Add:**
```
boto3
```
Add to `pyproject.toml` / `requirements.txt`.

**Environment Variables Required (add to `.env.example`):**
```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=ap-southeast-1
SES_FROM_EMAIL=no-reply@harinezumi.myddns.me
FRONTEND_URL=https://yourdomain.com
```

**Implementation:**
```python
import boto3
from app.core.config import settings

ses_client = boto3.client(
    "ses",
    region_name=settings.AWS_DEFAULT_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

def send_activation_email(to_email: str, activation_url: str) -> None:
    ses_client.send_email(
        Source=settings.SES_FROM_EMAIL,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": "Activate your account"},
            "Body": {
                "Html": {
                    "Data": f"""
                    <h3>Activate your account</h3>
                    <p>This link expires in 2 hours.</p>
                    <a href='{activation_url}'>Activate</a>
                    """
                }
            },
        },
    )
```

**Error Handling:**
- Catch `botocore.exceptions.ClientError` and log the error
- Do not raise to caller — registration must not fail if email delivery fails
- Log a warning if SES credentials are not configured

**Security Rules:**
- Credentials loaded exclusively from environment variables
- No credentials in source code or config files committed to VCS
- IAM user must have only `ses:SendEmail` and `ses:SendRawEmail` permissions (principle of least privilege)

**Acceptance Criteria:**
- `send_activation_email()` sends email via SES when credentials are valid
- Email `Subject`: `"Activate your account"`
- Email body contains the activation URL
- SES `ClientError` is caught and logged without crashing registration
- Missing credentials log a warning but do not prevent application startup

**Required Tests:**
- Unit test with mocked boto3 client: verify `send_email()` called with correct `Source`, `ToAddresses`, and URL in body
- Unit test: SES `ClientError` is caught and does not propagate

---

### Task BE-020-D: Modify Registration Flow

**Title:** Update `register_user()` to create inactive account and send activation email

**Files Affected:**
- `app/services/auth_service.py` — `register_user()`
- `app/repository/auth_repo.py` — `create_user()` (must accept new fields)

**Changed Registration Logic:**
1. Create user with `is_active=False`
2. Generate activation token: `secrets.token_urlsafe(32)`
3. Set `activation_expires_at = datetime.utcnow() + timedelta(hours=2)`
4. Persist `activation_token` and `activation_expires_at` to the user record
5. Build activation URL: `{FRONTEND_URL}/activate?token={token}`
6. Call `send_activation_email(user.email, activation_url)`
7. Return `TokenResponse` as before

**Database Impact:** New columns populated at registration time

**API Changes:**
- `POST /v1/auth/register` — response format unchanged
- Returned access token will be rejected by protected endpoints until activation (blocked in BE-020-F)

**Validation Rules:**
- Token must be `secrets.token_urlsafe(32)` (cryptographically secure, URL-safe)
- `activation_expires_at` must be `datetime.utcnow() + timedelta(hours=2)`

**Acceptance Criteria:**
- After registration: `is_active=False`, non-null `activation_token`, non-null `activation_expires_at`
- Activation email sent to registered address via SES
- Duplicate email registration still returns `400 Bad Request`

**Required Tests:**
- Unit test: registration produces inactive user with token and expiry set
- Unit test: `send_activation_email()` called with correct email and URL (mock SES)
- Unit test: email send failure does not cause registration to fail

---

### Task BE-020-E: Create Activation Endpoint

**Title:** Add `POST /v1/auth/activate` endpoint

**Files Affected:**
- `app/api/v1/auth.py`
- `app/services/auth_service.py` — add `activate_account(db, token)`
- `app/repository/auth_repo.py` — add `get_user_by_activation_token(db, token)`

**Endpoint Spec:**
```
POST /v1/auth/activate
Authentication: None required

Request Body:
  token: str (required)

Response 200:
  { "message": "Account activated successfully." }

Error Responses:
  400 — token not found: "Invalid activation token."
  400 — token expired: "Activation link has expired."
  400 — already active: "Account is already active."
```

**Activation Logic:**
1. Query user WHERE `activation_token = token` AND `deleted_at IS NULL`
2. Not found → `400 Bad Request: "Invalid activation token."`
3. `activation_expires_at < utcnow()` → `400 Bad Request: "Activation link has expired."`
4. `user.is_active = True` → `400 Bad Request: "Account is already active."`
5. Set `user.is_active = True`, `user.activation_token = None`, `user.activation_expires_at = None`
6. Commit → return `200 { "message": "Account activated successfully." }`

**Security:**
- Token is single-use; cleared immediately on successful activation
- Endpoint requires no authentication

**Acceptance Criteria:**
- Valid token → activated, token cleared, `200 OK`
- Invalid/unknown token → `400`
- Expired token → `400`
- Already active → `400`
- Replayed (used) token → `400` (token was cleared)

**Required Tests:**
- Unit test: valid token activates account and clears token fields
- Unit test: expired token returns 400
- Unit test: unknown token returns 400
- Unit test: already-active account returns 400
- Integration test: register → activate → verify `is_active = True`

---

### Task BE-020-F: Reject Inactive Users on Protected Endpoints

**Title:** Add `is_active` check to `get_current_user` dependency

**Files Affected:**
- `app/api/dependencies/auth.py` — `get_current_user()`

**Change:**
After loading the user from DB, add:
```python
if not current_user.is_active:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Account is not activated. Please check your email."
    )
```

**Placement:** After the existing user retrieval, before returning the user object.

**Database Impact:** None

**API Changes:**
- All `get_current_user`-protected endpoints return `403 Forbidden` for inactive users
- `/v1/auth/activate` must NOT use `get_current_user` — it is a public endpoint

**Acceptance Criteria:**
- Inactive user token on any protected endpoint → `403 Forbidden`
- Active user token → normal response
- `/v1/auth/activate` accessible without authentication

**Required Tests:**
- Unit test: inactive user → GET `/v1/me` returns `403`
- Unit test: active user → GET `/v1/me` returns `200`
- Integration test: register → call protected endpoint → `403` → activate → call protected endpoint → `200`

---

## 3. AWS SES Infrastructure Setup (DevOps / Pre-requisite)

> These steps must be completed by the infrastructure/DevOps team before BE-020-C can be tested in staging.

### Step 1: Verify Domain in SES
- Navigate to AWS SES → Verified Identities → Create Identity → Domain
- Add DNS records: DKIM (CNAME), SPF (TXT with `amazonses.com`)
- Confirm status: **Verified**

### Step 2: Request SES Production Access
- AWS SES → Account Dashboard → Request Production Access
- Use case: **Transactional email**
- Wait for AWS approval before sending to unverified recipients

### Step 3: Create IAM User for SES
- Create IAM user with programmatic access only
- Attach inline policy:
```json
{
  "Effect": "Allow",
  "Action": [
    "ses:SendEmail",
    "ses:SendRawEmail"
  ],
  "Resource": "*"
}
```
- Store `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in server environment (not in code)

### Step 4: Network Check
- Ensure outbound HTTPS (port 443) is open from on-prem server to AWS SES endpoints

### Step 5: Environment Configuration
```
AWS_ACCESS_KEY_ID=<from IAM>
AWS_SECRET_ACCESS_KEY=<from IAM>
AWS_DEFAULT_REGION=ap-southeast-1
SES_FROM_EMAIL=no-reply@harinezumi.myddns.me
FRONTEND_URL=https://yourdomain.com
```

---

## 4. Verification Checklist

- [ ] New user registers → receives activation email via SES
- [ ] Activation link valid → account activated, token cleared
- [ ] Activation link expired (>2h) → `400` error returned
- [ ] Expired/invalid token replayed → `400` error returned
- [ ] Inactive user calls any protected API → `403 Forbidden`
- [ ] Active user calls protected API → normal response
- [ ] Existing users (pre-migration) remain `is_active = TRUE`
- [ ] SES send failure does not break registration response
