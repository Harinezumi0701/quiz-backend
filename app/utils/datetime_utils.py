# app/utils/datetime_utils.py
from datetime import datetime
from typing import Optional


def datetime_to_timestamp(dt: Optional[datetime]) -> Optional[int]:
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
