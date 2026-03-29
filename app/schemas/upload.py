from pydantic import BaseModel, Field

from app.schemas.http_response import SuccessResponse


class PresignedUrlData(BaseModel):
    """Schema for presigned URL data"""
    url: str = Field(..., description="Presigned URL for uploading file", example="https://s3.example.com/presigned-url")
    key: str = Field(..., description="File key in S3 storage", example="uploads/file-123.jpg")
    public_url: str = Field(..., description="Public URL for accessing the file after upload", example="https://d2vp1l98shrrp4.cloudfront.net/uploads/file-123.jpg")
    expires_in: int = Field(..., description="URL expiration time in seconds", example=3600)


class PresignedUrlResponse(SuccessResponse[PresignedUrlData]):
    """Response schema for presigned URL"""
    pass


class PresignedUrlRequest(BaseModel):
    """Request schema for generating presigned URL"""
    filename: str = Field(..., min_length=1, description="Filename for the upload", example="image.jpg")
    prefix: str = Field("uploads", description="Prefix path for the file in S3 storage", example="uploads")
    content_type: str | None = Field(None, description="Content type of the file", example="image/jpeg")
    expires_in: int = Field(3600, ge=1, le=604800, description="URL expiration time in seconds (default: 3600, max: 604800)", example=3600)

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "image.jpg",
                "prefix": "uploads",
                "content_type": "image/jpeg",
                "expires_in": 3600
            }
        }
