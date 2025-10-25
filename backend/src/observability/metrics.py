"""
OpenTelemetry metrics configuration for Ras's Deep Treasure backend.

Sets up metrics collection with OTLP exporter to Prometheus.
Constitution: Explicit metrics with business-meaningful counters and histograms.
"""

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from config import get_settings

# Global meter instance
meter: metrics.Meter | None = None

# Pre-defined metrics (initialized after init_metrics())
action_counter: metrics.Counter | None = None
discovery_histogram: metrics.Histogram | None = None
surface_histogram: metrics.Histogram | None = None


def init_metrics() -> None:
    """
    Initialize OpenTelemetry metrics with OTLP exporter.

    Must be called during application startup (lifespan context).
    Only initializes if otel_metrics_enabled=True in settings.
    """
    global meter, action_counter, discovery_histogram, surface_histogram
    settings = get_settings()

    if not settings.otel_metrics_enabled:
        return

    # Create resource identifying this service
    resource = Resource.create(
        {
            "service.name": settings.otel_service_name,
            "service.version": "1.0.0",
        }
    )

    # Configure metric exporter
    otlp_exporter = OTLPMetricExporter(
        endpoint=f"{settings.otel_exporter_otlp_endpoint}/v1/metrics"
    )

    # Create periodic metric reader (export every 60 seconds)
    reader = PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=60000)

    # Configure meter provider
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)

    # Get meter instance
    meter = metrics.get_meter(__name__)

    # Create pre-defined metrics
    action_counter = meter.create_counter(
        name="game.actions.total",
        description="Total number of game actions performed",
        unit="1",
    )

    discovery_histogram = meter.create_histogram(
        name="game.discovery.duration",
        description="Discovery action duration in seconds",
        unit="s",
    )

    surface_histogram = meter.create_histogram(
        name="game.surface.duration",
        description="Surface action duration in seconds",
        unit="s",
    )


def get_meter() -> metrics.Meter:
    """
    Get OpenTelemetry meter instance.

    Returns:
        Meter: Active meter instance, or NoOp meter if metrics disabled.
    """
    if meter is None:
        # Return NoOp meter if metrics not initialized
        return metrics.get_meter(__name__)
    return meter


def record_action(action_type: str) -> None:
    """
    Record game action counter.

    Args:
        action_type: Type of action (e.g., "discover", "surface", "move").
    """
    if action_counter:
        action_counter.add(1, {"action": action_type})


def record_discovery_duration(duration_seconds: float) -> None:
    """
    Record discovery action duration.

    Args:
        duration_seconds: Duration of discovery action in seconds.
    """
    if discovery_histogram:
        discovery_histogram.record(duration_seconds)


def record_surface_duration(duration_seconds: float) -> None:
    """
    Record surface action duration.

    Args:
        duration_seconds: Duration of surface action in seconds.
    """
    if surface_histogram:
        surface_histogram.record(duration_seconds)
