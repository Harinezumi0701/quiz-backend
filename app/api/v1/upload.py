from fastapi import APIRouter, Depends, status
from app.schemas.upload import UploadRequest, UploadUrlResponse, UploadUrlData
from app.schemas.http_response import ErrorResponse
from app.services import upload_service
from app.api.dependencies.auth import get_current_user
from app.models.users import User

router = APIRouter()


@router.post(
    "",
    response_model=UploadUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate presigned upload URL",
    description="Generate a presigned S3 URL for uploading files and a CloudFront URL for access",
    responses={
        200: {
            "description": "Presigned URL generated successfully",
        },
        400: {
            "description": "Invalid content type or prefix",
            "model": ErrorResponse,
        },
        401: {
            "description": "Not authenticated",
            "model": ErrorResponse,
        },
        500: {
            "description": "S3 configuration error",
            "model": ErrorResponse,
        }
    }
)
def generate_upload_url(
    request: UploadRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a presigned URL for uploading files to S3.

    - **content_type**: MIME type of the file (e.g., "image/png", "image/jpeg")
    - **filename**: Original filename (used to extract extension)
    - **prefix**: Folder prefix for organizing files (e.g., "questions", "answers")
    - **expires_in**: URL expiration time in seconds (default: 3600, max: 86400)

    Returns:
    - **upload_url**: Presigned S3 URL for uploading (PUT request)
    - **key**: S3 object key
    - **public_url**: CloudFront URL for accessing the file after upload
    - **expires_in**: URL expiration time in seconds

    Usage:
    1. Call this endpoint to get the presigned URL
    2. Upload the file using PUT request to the upload_url with the file as body
    3. Use the public_url to access the file after upload
    """
    result = upload_service.generate_presigned_upload_url(
        content_type=request.content_type,
        filename=request.filename,
        prefix=request.prefix,
        expires_in=request.expires_in,
    )

    return UploadUrlResponse(
        data=UploadUrlData(**result),
        meta={}
    )
