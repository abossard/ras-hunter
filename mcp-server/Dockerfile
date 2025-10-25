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

# Install dependencies (no virtualenv, only production dependencies, with retries)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main \
    || poetry install --no-interaction --no-ansi --no-root --only main \
    || poetry install --no-interaction --no-ansi --no-root --only main

# Copy application code
COPY src/ ./src/

# Install the package
RUN poetry install --no-interaction --no-ansi --only main

# Expose MCP server port
EXPOSE 8001

# Run MCP server
CMD ["python", "-m", "src.server"]
