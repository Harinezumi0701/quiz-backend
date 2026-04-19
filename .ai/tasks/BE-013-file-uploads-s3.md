---
id: BE-013
title: File Uploads — S3 presigned URL generation
spec: spec/03-content-management.md#file-uploads
status: done
priority: medium
---

## Context
Images for questions and answer options are uploaded directly from browser to S3 to avoid routing large files through the API.

## Acceptance Criteria
- [x] `POST /uploads/` returns S3 presigned PUT URL + final CloudFront URL
- [x] Presigned URL scoped to specific key/prefix (not open-ended)
- [x] Invalid MIME types rejected
- [x] CloudFront URL stored in `image_url` field after upload

## Technical Notes
- `app/api/v1/upload.py`
- boto3 for presigned URL generation
- CloudFront domain configured via env/constants
