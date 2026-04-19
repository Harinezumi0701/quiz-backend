---
id: BE-008
title: Content — Question & answer option management
spec: spec/03-content-management.md#questions
status: done
priority: high
---

## Context
Questions and answer options are the building blocks of tests. They support rich text and images.

## Acceptance Criteria
- [x] CRUD `/questions/` — supports `is_multiple_choice` flag
- [x] CRUD `/answers/` — answer options with `is_correct` and `explanation`
- [x] `image_url` stored as CloudFront URL after S3 upload

## Technical Notes
- `app/api/v1/question.py`, `app/api/v1/answer.py`
- Rich text stored as serialized HTML or JSON (confirm format — Plate.js output)
