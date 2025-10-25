"""
OpenTelemetry tracer configuration for Ras's Deep Treasure backend.

Sets up distributed tracing with OTLP exporter to Jaeger.
Constitution: Explicit observability with conditional enablement.
"""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from config import get_settings

# Global tracer instance
tracer: trace.Tracer | None = None


def init_tracer() -> None:
    """
    Initialize OpenTelemetry tracer with OTLP exporter.

    Must be called during application startup (lifespan context).
    Only initializes if otel_traces_enabled=True in settings.
    """
    global tracer
    settings = get_settings()

    if not settings.otel_traces_enabled:
        return

    # Create resource identifying this service
    resource = Resource.create(
        {
            "service.name": settings.otel_service_name,
            "service.version": "1.0.0",
        }
    )

    # Configure tracer provider
    provider = TracerProvider(resource=resource)

    # Add OTLP exporter with batch processor
    otlp_exporter = OTLPSpanExporter(endpoint=f"{settings.otel_exporter_otlp_endpoint}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    # Get tracer instance
    tracer = trace.get_tracer(__name__)


def instrument_fastapi(app) -> None:
    """
    Instrument FastAPI app with OpenTelemetry.

    Args:
        app: FastAPI application instance.
    """
    settings = get_settings()
    if settings.otel_traces_enabled:
        FastAPIInstrumentor.instrument_app(app)


def get_tracer() -> trace.Tracer:
    """
    Get OpenTelemetry tracer instance.

    Returns:
        Tracer: Active tracer instance, or NoOp tracer if tracing disabled.
    """
    if tracer is None:
        # Return NoOp tracer if tracing not initialized
        return trace.get_tracer(__name__)
    return tracer
