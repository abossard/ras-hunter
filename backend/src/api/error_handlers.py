"""
Error handling module for Ras's Deep Treasure backend.

Provides consistent error responses with diagnostic context per FR-052.
Constitution: Diagnostic errors with structured error codes.
"""

from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from observability.logger import get_logger

logger = get_logger(__name__)


class ErrorResponse(BaseModel):
    """Standardized error response schema."""

    error_code: str
    message: str
    diagnostic: dict[str, Any] | None = None


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request object.
        exc: Validation exception.

    Returns:
        JSONResponse with standardized error format.
    """
    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "errors": exc.errors(),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "diagnostic": {
                "errors": exc.errors(),
                "body": str(exc.body) if exc.body else None,
            },
        },
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle HTTPException with diagnostic context.

    Args:
        request: FastAPI request object.
        exc: HTTP exception.

    Returns:
        JSONResponse with standardized error format.
    """
    from fastapi import HTTPException

    if isinstance(exc, HTTPException):
        # Check if detail is already in our error format
        if isinstance(exc.detail, dict) and "error_code" in exc.detail:
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.detail,
            )

        # Convert simple string detail to error format
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": "HTTP_ERROR",
                "message": str(exc.detail),
                "diagnostic": None,
            },
        )

    # Generic exception handling
    logger.error(
        "Unhandled exception",
        extra={
            "path": request.url.path,
            "exception": str(exc),
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An internal server error occurred",
            "diagnostic": {
                "type": type(exc).__name__,
                "details": str(exc),
            },
        },
    )
