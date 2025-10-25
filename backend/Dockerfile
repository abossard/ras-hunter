# Backend Dockerfile for Ras's Deep Treasure API
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (production only, no virtualenv in container, with retries)
RUN poetry config virtualenvs.create false \
    && (poetry install --no-interaction --no-ansi --no-root --only main \
        || poetry install --no-interaction --no-ansi --no-root --only main \
        || poetry install --no-interaction --no-ansi --no-root --only main)

# Copy application code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Add src to Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Install the package (makes src module importable)
RUN poetry install --no-interaction --no-ansi --only main

# Expose port
EXPOSE 8000

# Health check using curl
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run server (migrations will be run manually via docker exec when models are ready)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app/src"]
