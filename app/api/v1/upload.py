from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.schemas.upload import PresignedUrlRequest, PresignedUrlResponse, PresignedUrlData
from app.schemas.http_response import ErrorResponse
from app.services import s3_service
from app.db.session import get_db
from app.api.dependencies.permissions import require_permission
from app.models.users import User

router = APIRouter()


@router.post(
    "",
    response_model=PresignedUrlResponse,
    summary="Generate presigned URL for file upload",
    description="Generate a presigned URL for uploading files to S3 Storage",
    responses={
        200: {
            "description": "Presigned URL generated successfully",
        },
        400: {
            "description": "Invalid request or S3 configuration error",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
)
def generate_presigned_url(
    request: PresignedUrlRequest = Body(...),
    db: Session = Depends(get_db),
    _user: User = Depends(require_permission("questions::upload")),
):
    """
    Generate a presigned URL for uploading files to S3 Storage.

    - **filename**: Name of the file to upload (required)
    - **prefix**: Prefix path for the file in S3 storage (default: "uploads")
    - **content_type**: Optional content type of the file (e.g., 'image/jpeg', 'application/pdf')
    - **expires_in**: URL expiration time in seconds (default: 3600, max: 604800)

    Requires permission: questions::upload

    Returns a presigned URL that can be used to upload the file directly to S3 Storage.
    """
    try:
        presigned_url, file_key = s3_service.generate_presigned_url(
            filename=request.filename,
            prefix=request.prefix,
            content_type=request.content_type,
            expires_in=request.expires_in
        )
        
        return PresignedUrlResponse(
            data=PresignedUrlData(
                url=presigned_url,
                key=file_key,
                expires_in=request.expires_in
            ),
            meta={}
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate presigned URL: {str(e)}"
        )


@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    summary="Delete a file from S3 Storage",
    description="Delete a file from S3 Storage by file key",
    responses={
        200: {
            "description": "File deleted successfully",
        },
        404: {
            "description": "File not found",
            "model": ErrorResponse,
        },
        400: {
            "description": "Invalid request or S3 configuration error",
            "model": ErrorResponse,
        },
        403: {
            "description": "Permission denied",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
)
def delete_file(
    key: str = Query(..., description="File key in S3 storage", example="uploads/file-123.jpg"),
    db: Session = Depends(get_db),
    _user: User = Depends(require_permission("questions::delete")),
):
    """
    Delete a file from S3 Storage.

    - **key**: File key in S3 storage (required)

    Requires permission: questions::delete

    Returns success message if file was deleted successfully.
    """
    try:
        deleted = s3_service.delete_file(key)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with key {key} not found",
            )
        
        return {"message": "File deleted successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )
