# Spec 04 — Test Taking & Submissions

## Test Access

- Users see tests available to them via `GET /user-tests/`
- A test is available if: it is assigned to the user OR there is no assignment restriction (TBD — confirm with dev)
- Questions for a specific test: `GET /user-tests/{test_id}/questions`
- Questions are returned in a consistent order (question order within test — confirm if randomized)

---

## Test Session (Frontend)

The frontend manages all session state locally (no server-side session):

| State | Description |
|-------|-------------|
| `answers` | Map of `questionId → answerId[]` |
| `flagged` | Set of flagged `questionId`s |
| `currentIndex` | Active question number |
| `timeRemaining` | Countdown from `test.time_limit` |

### Timer Behavior

- Timer starts when test page loads
- Counts down in seconds
- At 0: auto-submit current answer state
- If `time_limit` is null: no timer shown, no auto-submit

---

## Submission

- `POST /tests/{id}/submit` with payload: array of `{ question_id, answer_ids[] }`
- Unanswered questions may be submitted with empty `answer_ids` or omitted (confirm expected behavior)
- Backend scores each answer and creates a `SubmissionHistory` record
- Returns the submission result (score, per-question correct/incorrect)

### Acceptance Criteria

- [ ] Submit correctly scores single-choice questions (one correct answer)
- [ ] Submit correctly scores multiple-choice (all correct options must be selected, no extra)
- [ ] Unanswered questions are recorded as incorrect
- [ ] A new `SubmissionHistory` is created on each submit (retakes allowed)
- [ ] Response includes: `total_questions`, `correct_count`, per-question `{ question_id, is_correct, correct_answer_ids }`

---

## Result Review

After submission, user sees a result review screen:

- Score summary: `correct / total` with percentage
- Filter questions by: All | Correct | Incorrect | Not Answered | Flagged
- Per question shows:
  - Question text (rich text)
  - User's selected answer(s) highlighted
  - Correct answer(s) highlighted
  - Explanation text (rich text, if provided)

### Acceptance Criteria

- [ ] Result page loads from latest submission for a test
- [ ] Historical submission accessible via `/tests/{id}/result/{submissionId}`
- [ ] Correct/incorrect state matches backend scoring
- [ ] Explanations render rich text correctly
- [ ] Question filter controls work correctly

---

## Test Assignments

- Admins assign tests to users via `POST /test-assignments/` or bulk `POST /test-assignments/bulk`
- Assignment has optional `expires_at` — after expiry, test becomes inaccessible
- `DELETE /test-assignments/{id}` removes an assignment
- Unique constraint: one assignment per `(user_id, test_id)` pair

### Acceptance Criteria

- [ ] Admin can assign a test to a user with optional expiry date
- [ ] Bulk assignment assigns one test to multiple users in one request
- [ ] Duplicate assignment returns a clear error (not a 500)
- [ ] Expired assignments hide the test from the user
