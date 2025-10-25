"""
JWT authentication service for Ras's Deep Treasure backend.

Handles token creation, verification, and user authentication.
Constitution: Explicit error handling with diagnostic context.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.config import get_settings

# Bearer token scheme for dependency injection
security_scheme = HTTPBearer()


def create_token(user_id: int, username: str) -> str:
    """
    Create JWT access token for authenticated user.

    Args:
        user_id: User database ID.
        username: Username for inclusion in token payload.

    Returns:
        Encoded JWT token string.
    """
    settings = get_settings()

    expiration = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiration_hours)

    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expiration,
        "iat": datetime.now(timezone.utc),
    }

    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


def verify_token(token: str) -> dict[str, any]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string to verify.

    Returns:
        Decoded token payload.

    Raises:
        HTTPException: If token is invalid or expired (401 Unauthorized with diagnostic context).
    """
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "INVALID_TOKEN",
                "message": "Authentication token is invalid or expired",
                "diagnostic": str(e),
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict[str, any]:
    """
    FastAPI dependency to extract authenticated user from JWT token.

    Args:
        credentials: Bearer token from Authorization header.

    Returns:
        Token payload containing user_id (as 'sub') and username.

    Raises:
        HTTPException: If token is invalid or missing (401 Unauthorized).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "MISSING_TOKEN",
                "message": "Authentication token is required",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(credentials.credentials)
    return payload


# Type alias for dependency injection
CurrentUser = Depends(get_current_user)
