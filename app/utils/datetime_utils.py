# app/utils/datetime_utils.py
from datetime import UTC, datetime


def normalize_to_utc(dt: datetime | None) -> datetime | None:
    """
    Normalize datetime to UTC timezone-aware datetime.
    
    If datetime is timezone-naive, assumes it's in UTC and adds UTC timezone.
    If datetime is timezone-aware, converts it to UTC.
    
    Args:
        dt: datetime object or None
        
    Returns:
        UTC timezone-aware datetime, or None if dt is None
    """
    if dt is None:
        return None
    
    # If already timezone-aware, convert to UTC
    if dt.tzinfo is not None:
        return dt.astimezone(UTC)
    
    # If timezone-naive, assume UTC and add timezone
    return dt.replace(tzinfo=UTC)


def datetime_to_timestamp(dt: datetime | None) -> int | None:
    """
    Convert datetime to Unix timestamp (seconds since epoch).
    
    Args:
        dt: datetime object or None
        
    Returns:
        Unix timestamp as integer, or None if dt is None
    """
    if dt is None:
        return None
    
    # Handle timezone-aware datetime
    if dt.tzinfo is not None:
        return int(dt.timestamp())
    
    # Handle timezone-naive datetime (assume UTC)
    return int(dt.timestamp())
