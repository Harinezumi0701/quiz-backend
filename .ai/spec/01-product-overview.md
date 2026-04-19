# Spec 01 — Product Overview

## Product Goal

A **quiz/test management platform** that enables administrators to create and assign tests, and allows users to take tests, track their performance, and review results.

---

## User Roles

| Role | Description |
|------|-------------|
| **Admin** | Manages categories, tests, questions, users, roles, and permissions. Can assign tests to users. |
| **User** | Takes assigned or available tests, views own results and history, manages own profile. |

> Roles are dynamic (stored in DB). The permission system uses `namespace::action` format with wildcard support.

---

## Core Feature Areas

| # | Feature Area | Description |
|---|--------------|-------------|
| 1 | Authentication | JWT-based login/register with refresh token rotation |
| 2 | Role & Permission Management | Dynamic roles with granular `namespace::action` permissions |
| 3 | User Management | Admin CRUD for users; users manage own profile |
| 4 | Category Management | Hierarchical grouping of tests |
| 5 | Test Management | Create/edit/publish tests with time limits; assign to users |
| 6 | Question Management | Single & multiple-choice questions with rich text and image support |
| 7 | Test Taking | Timer-based sessions, question flagging, auto-submit on timeout |
| 8 | Results & Review | Score summary, per-question review with correct answers and explanations |
| 9 | Dashboard & Analytics | Personal stats by overall, category, and test; recent submission history |
| 10 | File Uploads | S3 presigned URL uploads with CloudFront CDN delivery |

---

## Non-Functional Requirements

| Requirement | Detail |
|-------------|--------|
| API versioning | All endpoints under `/api/v1/` |
| Response format | Standardized `{data, meta}` for success; `{error}` for failures |
| Pagination | All list endpoints support page/size (max 100) + text search |
| Soft deletes | All entities use `deleted_at` rather than hard delete |
| Auth | JWT access token + refresh token; tokens stored and revoked in DB |
| Storage | AWS S3 for images; CloudFront for CDN delivery |
| i18n | Frontend supports English and Vietnamese |

---

## Out of Scope (v1)

- Public test sharing (no public links)
- Real-time collaboration / proctoring
- Payment / subscription management
- Mobile native apps
