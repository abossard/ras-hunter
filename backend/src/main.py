"""
Ras's Deep Treasure FastAPI application.

Main application entry point with middleware, error handlers, and lifecycle management.
Constitution: Explicit initialization with proper resource management.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.error_handlers import http_exception_handler, validation_exception_handler
from src.cache.redis_client import close_redis, init_redis
from src.config import get_settings
from src.database import close_db, init_db
from src.observability.logger import get_logger, init_logging
from src.observability.metrics import init_metrics
from src.observability.tracer import init_tracer, instrument_fastapi

# Initialize logging first
init_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles initialization and cleanup of database, cache, and observability.
    """
    settings = get_settings()
    logger.info(f"Starting {settings.otel_service_name}")

    # Initialize resources
    await init_db()
    await init_redis()
    init_tracer()
    init_metrics()

    logger.info("Application startup complete")

    yield

    # Cleanup resources
    logger.info("Shutting down application")
    await close_redis()
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Ras's Deep Treasure API",
    description="Multiplayer submarine treasure hunt game with fog-of-war",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Instrument with OpenTelemetry
instrument_fastapi(app)

# Register error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, http_exception_handler)


@app.get("/api/health", tags=["system"])
async def health_check():
    """
    Health check endpoint for load balancers.

    Returns:
        Status: "ok" if application is healthy.
    """
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint redirecting to API documentation.

    Returns:
        Redirect to /docs.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Ras's Deep Treasure API",
            "docs": "/docs",
            "health": "/api/health",
        },
    )
