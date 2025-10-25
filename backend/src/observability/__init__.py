"""Observability package."""

from src.observability.logger import get_logger, init_logging
from src.observability.metrics import (
    get_meter,
    init_metrics,
    record_action,
    record_discovery_duration,
    record_surface_duration,
)
from src.observability.tracer import get_tracer, init_tracer, instrument_fastapi

__all__ = [
    "init_tracer",
    "get_tracer",
    "instrument_fastapi",
    "init_metrics",
    "get_meter",
    "record_action",
    "record_discovery_duration",
    "record_surface_duration",
    "init_logging",
    "get_logger",
]
