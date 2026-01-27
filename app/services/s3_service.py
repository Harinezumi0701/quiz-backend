import os
import uuid
from typing import Optional
from dotenv import load_dotenv
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

load_dotenv()

S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION", "ap-southeast-1")
CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN", "")

DEFAULT_EXPIRES_IN = 3600
MAX_EXPIRES_IN = 604800


def get_s3_client():
    """Create and return S3 client"""
    if not all([S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
        raise ValueError("S3 configuration is incomplete. Please check environment variables.")

    return boto3.client(
        service_name="s3",
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        region_name=S3_REGION,
        config=Config(signature_version="s3v4"),
    )


def generate_presigned_url(
    filename: str,
    prefix: str = "uploads",
    content_type: Optional[str] = None,
    expires_in: int = DEFAULT_EXPIRES_IN
) -> tuple[str, str, str]:
    """
    Generate a presigned URL for uploading a file to S3 Storage.

    Args:
        filename: Original filename
        prefix: Prefix path for the file in S3 storage (default: "uploads")
        content_type: Content type of the file (e.g., 'image/jpeg')
        expires_in: URL expiration time in seconds (default: 3600, max: 604800)

    Returns:
        tuple: (presigned_url, file_key, public_url)

    Raises:
        ValueError: If S3 configuration is incomplete
        ClientError: If presigned URL generation fails
    """
    if expires_in > MAX_EXPIRES_IN:
        expires_in = MAX_EXPIRES_IN
    
    normalized_prefix = prefix.strip().strip('/')
    if normalized_prefix:
        normalized_prefix = normalized_prefix + '/'
    else:
        normalized_prefix = ""
    
    file_extension = os.path.splitext(filename)[1]
    file_key = f"{normalized_prefix}{uuid.uuid4()}{file_extension}"
    
    try:
        client = get_s3_client()
        
        params = {
            'Bucket': S3_BUCKET_NAME,
            'Key': file_key,
        }
        
        if content_type:
            params['ContentType'] = content_type
        
        presigned_url = client.generate_presigned_url(
            'put_object',
            Params=params,
            ExpiresIn=expires_in
        )
        
        if CLOUDFRONT_DOMAIN:
            public_url = f"https://{CLOUDFRONT_DOMAIN}/{file_key}"
        else:
            public_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{file_key}"

        return presigned_url, file_key, public_url
    
    except ClientError as e:
        raise Exception(f"Failed to generate presigned URL: {str(e)}")
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Unexpected error generating presigned URL: {str(e)}")


def delete_file(file_key: str) -> bool:
    """
    Delete a file from S3 Storage.
    
    Args:
        file_key: Key of the file to delete in S3 storage
    
    Returns:
        bool: True if file was deleted successfully, False if file not found
    
    Raises:
        ValueError: If S3 configuration is incomplete
        Exception: If file deletion fails
    """
    try:
        client = get_s3_client()
        
        try:
            client.head_object(Bucket=S3_BUCKET_NAME, Key=file_key)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404' or error_code == 'NoSuchKey':
                return False
            raise
        
        client.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_key
        )
        
        return True
    
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == '404' or error_code == 'NoSuchKey':
            return False
        raise Exception(f"Failed to delete file: {str(e)}")
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Unexpected error deleting file: {str(e)}")
