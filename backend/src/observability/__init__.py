"""Observability package."""

from observability.logger import get_logger, init_logging
from observability.metrics import (
    get_meter,
    init_metrics,
    record_action,
    record_discovery_duration,
    record_surface_duration,
)
from observability.tracer import get_tracer, init_tracer, instrument_fastapi

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
