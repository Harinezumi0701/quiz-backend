# app/utils/user_id_generator.py
import random
import string

from sqlalchemy.orm import Session

from app.models.users import User


def generate_user_id() -> str:
    """
    Generate a random user_id matching regex [A-Za-z\._-]{6}
    
    Returns:
        A 6-character string containing only letters, dots, underscores, and hyphens
    """
    # Characters allowed: A-Z, a-z, ., _, -
    allowed_chars = string.ascii_letters + '._-'
    return ''.join(random.choice(allowed_chars) for _ in range(6))


def generate_unique_user_id(db: Session, max_attempts: int = 100) -> str:
    """
    Generate a unique user_id that doesn't exist in the database.
    
    Args:
        db: Database session
        max_attempts: Maximum number of attempts to generate a unique ID
        
    Returns:
        A unique 6-character user_id
        
    Raises:
        RuntimeError: If unable to generate a unique ID after max_attempts
    """
    for _ in range(max_attempts):
        user_id = generate_user_id()
        existing_user = db.query(User).filter(User.user_id == user_id).first()
        if not existing_user:
            return user_id
    
    raise RuntimeError(f"Unable to generate unique user_id after {max_attempts} attempts")
