# Ras's Deep Treasure - Docker Compose Setup

Complete containerized deployment of Ras's Deep Treasure multiplayer submarine game.

## Architecture

This docker-compose stack includes:

### Core Application Services
- **Backend API** (FastAPI): Port 8000 - REST API and WebSocket server
- **MCP Server**: Port 8001 - AI agent interface wrapping the backend API
- **Frontend** (React): Port 5173 - Web UI served via Nginx

### Infrastructure Services
- **PostgreSQL 15**: Port 5432 - Primary database
- **Redis 7**: Port 6379 - Cache and pub/sub

### Observability Stack
- **Jaeger**: Port 16686 - Distributed tracing UI
- **Prometheus**: Port 9090 - Metrics collection
- **Grafana**: Port 3001 - Dashboards and visualization

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available for containers

### Start All Services

```bash
# Build and start all services
docker-compose up --build

# Start in detached mode (background)
docker-compose up -d --build
```

### Check Service Health

```bash
# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Check service status
docker-compose ps
```

### Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Frontend UI | http://localhost:5173 | Register new user |
| MCP Server | http://localhost:8001 | - |
| Jaeger UI | http://localhost:16686 | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3001 | admin/admin |

### Stop Services

```bash
# Stop all services (keep data)
docker-compose stop

# Stop and remove containers (keep data)
docker-compose down

# Stop and remove everything including volumes (⚠️ DELETES DATA)
docker-compose down -v
```

## Development Workflow

### Rebuild Specific Service

```bash
# Rebuild backend after code changes
docker-compose up -d --build backend

# Rebuild frontend
docker-compose up -d --build frontend

# Rebuild MCP server
docker-compose up -d --build mcp-server
```

### Database Operations

```bash
# Run migrations
docker-compose exec backend poetry run alembic upgrade head

# Create new migration
docker-compose exec backend poetry run alembic revision -m "description"

# Access PostgreSQL shell
docker-compose exec postgres psql -U ras_hunter -d ras_hunter
```

### Redis Operations

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Clear all cache
docker-compose exec redis redis-cli FLUSHALL
```

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service with timestamps
docker-compose logs -f --timestamps backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

## Environment Configuration

### Backend Environment Variables

Edit `docker-compose.yml` to customize:

```yaml
environment:
  # Database
  DATABASE_URL: postgresql+asyncpg://ras_hunter:dev_password@postgres:5432/ras_hunter
  
  # Game Configuration
  MAP_SIZE: 32
  MAX_PLAYERS: 20
  OXYGEN_MAX: 20
  DISCOVERY_COOLDOWN_SECONDS: 8
  
  # Security
  JWT_SECRET: change-me-in-production-min-32-characters-required
  
  # Observability
  OTEL_TRACES_ENABLED: "true"
  OTEL_METRICS_ENABLED: "true"
  LOG_LEVEL: INFO
```

### Production Deployment

For production, create a `docker-compose.prod.yml`:

```bash
# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Production checklist:**
- [ ] Change `JWT_SECRET` to secure random value (32+ characters)
- [ ] Change database password
- [ ] Set `RELOAD: "false"`
- [ ] Configure proper `CORS_ORIGINS`
- [ ] Set `LOG_LEVEL: WARNING` or `ERROR`
- [ ] Use external PostgreSQL/Redis for high availability
- [ ] Configure backup strategy for volumes
- [ ] Set up SSL/TLS termination (reverse proxy)
- [ ] Configure resource limits (CPU/memory)

## Volumes

Persistent data stored in Docker volumes:

- `postgres-data`: Database files
- `redis-data`: Redis persistence
- `prometheus-data`: Metrics history
- `grafana-data`: Dashboards and settings

### Backup Volumes

```bash
# Backup PostgreSQL data
docker-compose exec postgres pg_dump -U ras_hunter ras_hunter > backup.sql

# Restore from backup
docker-compose exec -T postgres psql -U ras_hunter -d ras_hunter < backup.sql
```

## Networking

Two Docker networks:

- `ras-hunter-network`: Core application services
- `observability`: Monitoring stack (isolated)

Services communicate using container names as hostnames:
- Backend → `postgres:5432`
- Backend → `redis:6379`
- Frontend → `backend:8000`
- MCP Server → `backend:8000`

## Troubleshooting

### Backend won't start

```bash
# Check database connection
docker-compose exec backend poetry run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"

# Verify migrations
docker-compose exec backend poetry run alembic current
docker-compose exec backend poetry run alembic upgrade head
```

### Database connection errors

```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U ras_hunter

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Frontend can't reach backend

1. Check backend health: `curl http://localhost:8000/api/health`
2. Verify CORS configuration in `docker-compose.yml`
3. Check browser console for CORS errors
4. Ensure `VITE_API_BASE_URL` matches exposed backend port

### Observability not working

```bash
# Check Jaeger connection
curl http://localhost:4318/v1/traces

# Verify OpenTelemetry configuration
docker-compose exec backend env | grep OTEL

# Restart observability stack
docker-compose restart jaeger prometheus grafana
```

## Testing

### Run Tests in Containers

```bash
# Backend unit tests
docker-compose exec backend poetry run pytest tests/unit/

# Backend integration tests
docker-compose exec backend poetry run pytest tests/integration/

# Contract tests
docker-compose exec backend poetry run pytest tests/contract/

# All tests with coverage
docker-compose exec backend poetry run pytest --cov=src --cov-report=html
```

### E2E Tests (Playwright)

E2E tests run against the running stack:

```bash
# Install E2E dependencies (if npm available locally)
cd tests/e2e && npm install

# Run E2E tests against docker stack
npm run test

# Run with UI
npm run test -- --ui
```

## Resource Usage

Typical resource consumption:

| Service | CPU (idle) | Memory |
|---------|------------|--------|
| Backend | ~5% | 200MB |
| MCP Server | ~2% | 100MB |
| Frontend | ~1% | 50MB |
| PostgreSQL | ~3% | 150MB |
| Redis | ~1% | 50MB |
| Jaeger | ~5% | 300MB |
| Prometheus | ~3% | 200MB |
| Grafana | ~2% | 150MB |

**Total:** ~1.2GB RAM (idle), scales with concurrent players

## Monitoring

### Key Metrics (Prometheus)

- `game_actions_total`: Counter of all game actions
- `game_discovery_duration`: Discovery operation latency
- `game_surface_duration`: Surface operation latency
- `http_requests_total`: API request counter
- `http_request_duration_seconds`: API latency histogram

### Grafana Dashboards

1. Open http://localhost:3001 (admin/admin)
2. Navigate to Dashboards
3. Create dashboard with Prometheus data source
4. Import sample queries:
   - Active players: `count(game_submarine_oxygen > 0)`
   - Discoveries per minute: `rate(game_actions_total{action="discover"}[1m])`
   - API latency p95: `histogram_quantile(0.95, http_request_duration_seconds_bucket)`

### Distributed Tracing (Jaeger)

1. Open http://localhost:16686
2. Select service: `ras-hunter-backend`
3. Search for traces
4. Inspect discovery/surface operation spans
5. Analyze latency and dependencies

## Scaling

### Horizontal Scaling (Multiple Backend Instances)

```yaml
# In docker-compose.yml
backend:
  deploy:
    replicas: 3
  # Add load balancer (nginx/traefik) in front
```

### Database Connection Pool Tuning

```yaml
# Adjust based on load
REDIS_MAX_CONNECTIONS: 20  # Default: 10
# PostgreSQL pool_size configured in backend/src/database.py
```

## CI/CD Integration

GitHub Actions workflow example:

```yaml
- name: Build and test
  run: |
    docker-compose up -d --build
    docker-compose exec -T backend poetry run pytest
    docker-compose down -v
```

## Support

- Issues: GitHub repository issues
- Documentation: `/specs/001-deep-treasure-game/`
- API Docs: http://localhost:8000/docs (when running)
