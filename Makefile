.PHONY: help build up down restart logs ps clean test migrate shell

# Default target
help:
	@echo "Ras's Deep Treasure - Development Commands"
	@echo ""
	@echo "Docker Compose:"
	@echo "  make build          Build all services"
	@echo "  make up             Start all services"
	@echo "  make down           Stop all services"
	@echo "  make restart        Restart all services"
	@echo "  make logs           View logs (all services)"
	@echo "  make ps             Show service status"
	@echo "  make clean          Remove containers and volumes"
	@echo ""
	@echo "Database:"
	@echo "  make migrate        Run database migrations"
	@echo "  make migration      Create new migration (MSG='description')"
	@echo "  make db-shell       Open PostgreSQL shell"
	@echo "  make redis-shell    Open Redis CLI"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run backend tests"
	@echo "  make test-unit      Run unit tests only"
	@echo "  make test-integration  Run integration tests only"
	@echo "  make test-contract  Run contract tests only"
	@echo "  make test-e2e       Run end-to-end tests"
	@echo "  make coverage       Run tests with coverage report"
	@echo ""
	@echo "Development:"
	@echo "  make shell          Open backend shell"
	@echo "  make lint           Run code linters"
	@echo "  make format         Format code"
	@echo ""
	@echo "Monitoring:"
	@echo "  make jaeger         Open Jaeger UI"
	@echo "  make grafana        Open Grafana"
	@echo "  make prometheus     Open Prometheus"

# Docker Compose Commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started. Access:"
	@echo "  Frontend:   http://localhost:5173"
	@echo "  Backend:    http://localhost:8000"
	@echo "  API Docs:   http://localhost:8000/docs"
	@echo "  Jaeger UI:  http://localhost:16686"
	@echo "  Grafana:    http://localhost:3001"
	@echo "  Prometheus: http://localhost:9090"

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-mcp:
	docker-compose logs -f mcp-server

ps:
	docker-compose ps

clean:
	docker-compose down -v
	@echo "⚠️  All containers and volumes removed!"

# Database Commands
migrate:
	docker-compose exec backend poetry run alembic upgrade head

migration:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: MSG is required. Usage: make migration MSG='description'"; \
		exit 1; \
	fi
	docker-compose exec backend poetry run alembic revision -m "$(MSG)"

db-shell:
	docker-compose exec postgres psql -U ras_hunter -d ras_hunter

redis-shell:
	docker-compose exec redis redis-cli

db-reset:
	docker-compose exec backend poetry run alembic downgrade base
	docker-compose exec backend poetry run alembic upgrade head

# Testing Commands
test:
	docker-compose exec backend poetry run pytest

test-unit:
	docker-compose exec backend poetry run pytest tests/unit/

test-integration:
	docker-compose exec backend poetry run pytest tests/integration/

test-contract:
	docker-compose exec backend poetry run pytest tests/contract/

test-e2e:
	cd tests/e2e && npm run test

coverage:
	docker-compose exec backend poetry run pytest --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report: backend/htmlcov/index.html"

# Development Commands
shell:
	docker-compose exec backend /bin/bash

shell-mcp:
	docker-compose exec mcp-server /bin/bash

lint:
	docker-compose exec backend poetry run ruff check src/
	docker-compose exec backend poetry run mypy src/

lint-fix:
	docker-compose exec backend poetry run ruff check --fix src/

format:
	docker-compose exec backend poetry run black src/
	docker-compose exec backend poetry run isort src/

# Monitoring URLs
jaeger:
	@open http://localhost:16686 || xdg-open http://localhost:16686 || echo "Open http://localhost:16686"

grafana:
	@open http://localhost:3001 || xdg-open http://localhost:3001 || echo "Open http://localhost:3001 (admin/admin)"

prometheus:
	@open http://localhost:9090 || xdg-open http://localhost:9090 || echo "Open http://localhost:9090"

api-docs:
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || echo "Open http://localhost:8000/docs"

# Local Development (without Docker)
dev-backend:
	cd backend && poetry run uvicorn src.main:app --reload

dev-frontend:
	cd frontend && npm run dev

dev-mcp:
	cd mcp-server && poetry run python -m src.server

# Installation
install-backend:
	cd backend && poetry install

install-frontend:
	cd frontend && npm install

install-mcp:
	cd mcp-server && poetry install

install-e2e:
	cd tests/e2e && npm install

install-all: install-backend install-frontend install-mcp install-e2e
