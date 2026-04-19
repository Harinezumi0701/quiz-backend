---
id: BE-011
title: Submission — Scoring and history
spec: spec/04-test-taking.md#submission
status: done
priority: high
---

## Context
When a user submits a test, each answer is scored and persisted. History allows retakes and result review.

## Acceptance Criteria
- [x] `POST /tests/{id}/submit` scores answers and creates `SubmissionHistory` + `Submission` records
- [x] Single-choice: correct only if user selected the one correct answer
- [x] Multiple-choice: correct only if user selected ALL correct answers and NO incorrect ones
- [x] Unanswered questions recorded as incorrect
- [x] Response includes per-question `is_correct` and `correct_answer_ids`
- [x] Retakes allowed (new `SubmissionHistory` each time)

## Technical Notes
- Scoring logic: `app/services/test_service.py` or `submission_service.py`
- `SubmissionHistory` links to multiple `Submission` rows (one per question)
