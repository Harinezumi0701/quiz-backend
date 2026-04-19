# Spec 03 — Content Management

## Categories

- Flat list of named categories (no hierarchy in v1)
- Fields: `name`
- Used to group tests and questions
- Endpoints: CRUD `/categories/`, GET `/categories/{id}/questions`

### Acceptance Criteria

- [ ] Admin can create, edit, delete categories
- [ ] Listing returns all active (non-deleted) categories
- [ ] Deleting a category with active tests should return a clear error (or cascade — confirm with dev)

---

## Tests

- A test belongs to one category
- Fields: `name`, `category_id`, `description` (rich text), `time_limit` (seconds, nullable = untimed)
- Tests can be assigned to specific users via `UserTestAssignment`
- Endpoints: CRUD `/tests/`, POST `/tests/{id}/submit`

### Acceptance Criteria

- [ ] Admin can create, edit, delete tests
- [ ] Test list supports filtering by category and text search
- [ ] `time_limit = null` means the test is untimed
- [ ] A test must have at least one question before it can be taken (validated at submit time or list time — confirm)

---

## Questions

- A question belongs to one test (and optionally a category for standalone browsing)
- Fields: `content` (rich text), `image_url` (optional), `category_id`, `test_id`, `is_multiple_choice`
- `is_multiple_choice: true` → user can select multiple answers
- Endpoints: CRUD `/questions/`

### Acceptance Criteria

- [ ] Admin can create, edit, delete questions
- [ ] Each question has at least 2 answer options (validation — confirm count)
- [ ] Exactly one correct answer required for single-choice; one or more for multiple-choice
- [ ] Rich text (`content`) rendered correctly on frontend

---

## Answer Options

- An answer option belongs to one question
- Fields: `question_id`, `content` (rich text), `image_url` (optional), `is_correct`, `explanation` (rich text, shown after submission)
- Endpoints: CRUD `/answers/`

### Acceptance Criteria

- [ ] Admin can add/edit/delete answer options per question
- [ ] `is_correct` must be set on at least one option per question
- [ ] `explanation` is shown to user during result review (after test submission)

---

## File Uploads

- Images are uploaded directly from browser to S3 via presigned URL
- Flow: `POST /uploads/` → returns presigned S3 URL → browser PUTs file to S3 → stores CloudFront URL in `image_url`
- Accepted types: image files only (enforce MIME type)

### Acceptance Criteria

- [ ] `POST /uploads/` returns a valid S3 presigned URL
- [ ] Uploaded image URL (CloudFront) can be stored on question or answer option
- [ ] Invalid file types are rejected
