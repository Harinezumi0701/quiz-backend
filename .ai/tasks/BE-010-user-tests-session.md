---
id: BE-010
title: User Tests — Browse and fetch test questions
spec: spec/04-test-taking.md#test-access
status: done
priority: high
---

## Context
Users need to see their available tests and load questions to start a session.

## Acceptance Criteria
- [x] `GET /user-tests/` — list tests accessible to the current user
- [x] `GET /user-tests/{test_id}/questions` — return all questions + answer options for a test
- [x] Expired assignments excluded from list
- [x] Questions returned in consistent order

## Technical Notes
- `app/api/v1/user_tests.py`
- Answer options returned with question (nested), but `is_correct` must NOT be exposed to user before submission
