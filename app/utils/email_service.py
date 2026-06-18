# app/utils/email_service.py
import logging
import os

import boto3
import botocore.exceptions
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-southeast-1")
SES_FROM_EMAIL = os.getenv("SES_FROM_EMAIL", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def _get_ses_client():
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        logger.warning("AWS SES credentials are not configured — emails will not be sent")
        return None
    return boto3.client(
        "ses",
        region_name=AWS_DEFAULT_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def send_activation_email(to_email: str, activation_url: str) -> None:
    """Send account activation email via AWS SES.

    Errors are caught and logged; registration is never failed due to email delivery issues.
    """
    ses_client = _get_ses_client()
    if ses_client is None:
        return

    try:
        ses_client.send_email(
            Source=SES_FROM_EMAIL,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": "Activate your account"},
                "Body": {
                    "Html": {
                        "Data": f"""
                        <h3>Activate your account</h3>
                        <p>Click the link below to activate your account. This link expires in 2 hours.</p>
                        <a href='{activation_url}'>Activate your account</a>
                        <p>If you did not register, please ignore this email.</p>
                        """
                    }
                },
            },
        )
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to send activation email to %s: %s", to_email, exc)
