"""
Password hashing service for Ras's Deep Treasure backend.

Uses bcrypt for secure password hashing with configurable work factor.
Constitution: Explicit security with proper work factor tuning.
"""

from passlib.context import CryptContext

# Bcrypt context with work factor 12 (per security requirements)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt with work factor 12.

    Args:
        password: Plain-text password to hash.

    Returns:
        Hashed password string (bcrypt format).
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against bcrypt hash.

    Args:
        plain_password: Plain-text password from user input.
        hashed_password: Stored bcrypt hash from database.

    Returns:
        True if password matches hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
