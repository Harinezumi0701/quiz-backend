---
id: BE-006
title: Content — Category management
spec: spec/03-content-management.md#categories
status: done
priority: medium
---

## Context
Categories group tests for browsing and analytics breakdown.

## Acceptance Criteria
- [x] CRUD `/categories/`
- [x] `GET /categories/{id}/questions` — list questions belonging to category
- [x] Soft delete on category

## Technical Notes
- `app/api/v1/category.py`
- Consider referential integrity: deleting a category with tests — check current behavior
