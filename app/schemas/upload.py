from pydantic import BaseModel, Field
from app.schemas.http_response import SuccessResponse


class UploadRequest(BaseModel):
    """Request schema for generating presigned upload URL"""
    content_type: str = Field(
        ...,
        description="MIME type of the file",
        example="image/png"
    )
    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original filename",
        example="example.png"
    )
    prefix: str = Field(
        default="uploads",
        description="Folder prefix for the upload",
        example="questions"
    )
    expires_in: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="URL expiration time in seconds (60-86400)",
        example=3600
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content_type": "image/png",
                "filename": "example.png",
                "prefix": "questions",
                "expires_in": 3600
            }
        }


class UploadUrlData(BaseModel):
    """Data schema for presigned upload URL response"""
    upload_url: str = Field(
        ...,
        description="Presigned S3 URL for uploading the file",
        example="https://bucket.s3.region.amazonaws.com/questions/abc123.png?X-Amz-Signature=..."
    )
    key: str = Field(
        ...,
        description="S3 object key",
        example="questions/abc123.png"
    )
    public_url: str = Field(
        ...,
        description="CloudFront URL for accessing the file after upload",
        example="https://d1234abcd.cloudfront.net/questions/abc123.png"
    )
    expires_in: int = Field(
        ...,
        description="URL expiration time in seconds",
        example=3600
    )

    class Config:
        json_schema_extra = {
            "example": {
                "upload_url": "https://bucket.s3.ap-southeast-1.amazonaws.com/questions/abc123.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Signature=...",
                "key": "questions/abc123.png",
                "public_url": "https://d1234abcd.cloudfront.net/questions/abc123.png",
                "expires_in": 3600
            }
        }


class UploadUrlResponse(SuccessResponse[UploadUrlData]):
    """Response schema for presigned upload URL"""
    pass
