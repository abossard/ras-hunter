"""
Structured logging configuration for Ras's Deep Treasure backend.

Provides JSON-formatted logging with trace_id injection for correlation.
Constitution: Diagnostic errors with structured context.
"""

import logging
import sys
from typing import Any

from opentelemetry import trace

from src.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter with trace_id injection."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format.

        Returns:
            JSON-formatted log string.
        """
        import json

        # Extract trace context if available
        span = trace.get_current_span()
        trace_id = None
        span_id = None

        if span and span.is_recording():
            ctx = span.get_span_context()
            trace_id = f"{ctx.trace_id:032x}"
            span_id = f"{ctx.span_id:016x}"

        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add trace context if available
        if trace_id:
            log_data["trace_id"] = trace_id
        if span_id:
            log_data["span_id"] = span_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter for development."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as readable text.

        Args:
            record: Log record to format.

        Returns:
            Formatted log string.
        """
        # Extract trace context if available
        span = trace.get_current_span()
        trace_id = ""

        if span and span.is_recording():
            ctx = span.get_span_context()
            trace_id = f" [trace: {ctx.trace_id:032x}]"

        return (
            f"{self.formatTime(record, self.datefmt)} "
            f"{record.levelname:<8} "
            f"{record.name}: "
            f"{record.getMessage()}"
            f"{trace_id}"
        )


def init_logging() -> None:
    """
    Initialize application logging.

    Must be called during application startup (lifespan context).
    """
    settings = get_settings()

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level))

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.log_level))

    # Set formatter based on configuration
    if settings.log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter(datefmt="%Y-%m-%d %H:%M:%S")

    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance for module.

    Args:
        name: Logger name (typically __name__ from calling module).

    Returns:
        Logger: Logger instance.
    """
    return logging.getLogger(name)
