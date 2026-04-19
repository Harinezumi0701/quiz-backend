# Spec 06 — Dashboard & Analytics

## Dashboard (`GET /me/dashboard`)

Returns aggregated stats for the currently authenticated user:

| Stat Group | Fields |
|------------|--------|
| Overall | `total_tests_taken`, `total_questions_answered`, `overall_accuracy` (%) |
| By Category | `category_id`, `category_name`, `tests_taken`, `accuracy` (%) |
| By Test | `test_id`, `test_name`, `attempts`, `best_score` (%), `last_score` (%) |
| Recent Activity | Last N submissions with date and score |

### Acceptance Criteria

- [ ] Dashboard returns data for the authenticated user only
- [ ] `overall_accuracy` = total correct / total answered (not per-test average)
- [ ] Category and test breakdowns include all tests the user has attempted
- [ ] No data returns empty arrays (not null) for category/test breakdowns

---

## Submission History (`GET /me/submission-history`)

- Paginated list of past submissions
- Each item: `submission_date`, `test_name`, `score` (%), `correct_count`, `total_questions`
- Sorted by `submitted_at` descending (most recent first)
- Supports standard pagination params (`page`, `size`)

### Acceptance Criteria

- [ ] Returns only submissions for the authenticated user
- [ ] Paginated with correct `total`, `page`, `size` in meta
- [ ] Each record links to the full submission result view
