"""
Configuration module for Ras's Deep Treasure backend.

Loads environment variables and provides application configuration.
Constitution: Explicit configuration with clear defaults and validation.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database Configuration
    database_url: str = "postgresql+asyncpg://ras_hunter:dev_password@localhost:5432/ras_hunter"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 10

    # JWT Authentication
    jwt_secret: str = "change-me-in-production-min-32-characters-required"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False

    # Game Configuration
    map_size: int = 32
    max_players: int = 20
    oxygen_max: int = 20
    discovery_cooldown_seconds: int = 8
    surface_duration_seconds: int = 60
    inactivity_timeout_minutes: int = 10

    # OpenTelemetry Configuration
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    otel_service_name: str = "ras-hunter-backend"
    otel_traces_enabled: bool = False
    otel_metrics_enabled: bool = False

    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "text"] = "json"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Settings: Application configuration instance.
    """
    return Settings()
