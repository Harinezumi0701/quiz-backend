import uuid
import boto3
from botocore.config import Config
from fastapi import HTTPException, status

from app.constants.storage import (
    S3_BUCKET_NAME,
    S3_REGION,
    S3_ACCESS_KEY_ID,
    S3_SECRET_ACCESS_KEY,
    CLOUDFRONT_DOMAIN,
    ALLOWED_CONTENT_TYPES,
    ALLOWED_PREFIXES,
    DEFAULT_EXPIRES_IN,
    MAX_EXPIRES_IN,
)


def get_s3_client():
    """Create and return S3 client."""
    if not S3_ACCESS_KEY_ID or not S3_SECRET_ACCESS_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3 credentials not configured"
        )

    return boto3.client(
        "s3",
        region_name=S3_REGION,
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4")
    )


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    if "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    return ""


def generate_unique_key(prefix: str, filename: str) -> str:
    """Generate unique S3 key with UUID."""
    extension = get_file_extension(filename)
    unique_id = uuid.uuid4().hex[:12]
    if extension:
        return f"{prefix}/{unique_id}.{extension}"
    return f"{prefix}/{unique_id}"


def generate_presigned_upload_url(
    content_type: str,
    filename: str,
    prefix: str = "uploads",
    expires_in: int = DEFAULT_EXPIRES_IN
) -> dict:
    """
    Generate presigned URL for uploading file to S3.

    Args:
        content_type: MIME type of the file
        filename: Original filename
        prefix: Folder prefix (e.g., "questions", "answers")
        expires_in: URL expiration time in seconds

    Returns:
        dict with upload_url, key, public_url, expires_in
    """
    # Validate content type
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content type '{content_type}' not allowed. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    # Validate prefix
    if prefix not in ALLOWED_PREFIXES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prefix '{prefix}' not allowed. Allowed prefixes: {', '.join(ALLOWED_PREFIXES)}"
        )

    # Validate expires_in
    if expires_in > MAX_EXPIRES_IN:
        expires_in = MAX_EXPIRES_IN

    # Validate S3 bucket
    if not S3_BUCKET_NAME:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3 bucket not configured"
        )

    # Generate unique key
    key = generate_unique_key(prefix, filename)

    # Get S3 client
    s3_client = get_s3_client()

    # Generate presigned PUT URL
    upload_url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )

    # Generate public URL (CloudFront or S3)
    if CLOUDFRONT_DOMAIN:
        public_url = f"https://{CLOUDFRONT_DOMAIN}/{key}"
    else:
        public_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{key}"

    return {
        "upload_url": upload_url,
        "key": key,
        "public_url": public_url,
        "expires_in": expires_in,
    }
