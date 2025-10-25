FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (no virtualenv needed in container)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY src/ ./src/

# Install the package
RUN poetry install --no-interaction --no-ansi

# Expose MCP server port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run MCP server
CMD ["python", "-m", "src.server"]
