---
id: BE-012
title: Dashboard — Analytics and submission history
spec: spec/06-analytics.md
status: done
priority: medium
---

## Context
Users want to see their performance at a glance — overall, by category, and by test.

## Acceptance Criteria
- [x] `GET /me/dashboard` returns: overall stats, per-category breakdown, per-test breakdown, recent activity
- [x] `GET /me/submission-history` returns paginated submission list (most recent first)
- [x] Data scoped strictly to authenticated user
- [x] Empty state returns `[]` not `null`

## Technical Notes
- `app/api/v1/me.py`
- Aggregate queries in `app/repository/` or `app/services/`
- `overall_accuracy` = sum(correct) / sum(answered) across all submissions
