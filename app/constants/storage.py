import os

# S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
S3_REGION = os.getenv("S3_REGION", "ap-southeast-1")
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", "")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "")

# CloudFront Configuration
CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN", "")  # e.g., "d1234abcd.cloudfront.net"

# Upload settings
ALLOWED_CONTENT_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml",
]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_EXPIRES_IN = 3600  # 1 hour
MAX_EXPIRES_IN = 86400  # 24 hours

# Allowed prefixes for uploads
ALLOWED_PREFIXES = ["questions", "answers", "categories", "tests", "users"]
