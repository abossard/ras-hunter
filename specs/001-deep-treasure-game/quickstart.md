# Quickstart: Ras's Deep Treasure Game

**Local Development Setup** (15 minutes)

## Prerequisites

Install the following on your development machine:

| Tool | Version | Purpose | Install Command |
|------|---------|---------|-----------------|
| **Python** | 3.11+ | Backend & MCP server | [python.org/downloads](https://www.python.org/downloads/) |
| **Node.js** | 18+ LTS | Frontend tooling | [nodejs.org](https://nodejs.org/) |
| **PostgreSQL** | 15+ | Persistent database | `brew install postgresql@15` (macOS) |
| **Redis** | 7+ | Cache & pub/sub | `brew install redis` (macOS) |
| **Poetry** | 1.5+ | Python dependency manager | `pip install poetry` |
| **Docker** (optional) | 24+ | Observability stack | [docker.com/get-started](https://www.docker.com/get-started/) |

**Verify installations**:
```bash
python --version  # Should show 3.11+
node --version    # Should show 18+
psql --version    # Should show 15+
redis-server --version  # Should show 7+
poetry --version  # Should show 1.5+
```

---

## Project Structure

```
ras-hunter/
├── backend/                 # FastAPI REST API
│   ├── src/
│   │   ├── models/         # SQLAlchemy entities
│   │   ├── services/       # Business logic
│   │   ├── api/            # Route handlers
│   │   ├── cache/          # Redis operations
│   │   ├── observability/  # OpenTelemetry setup
│   │   └── main.py         # FastAPI app entry
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   └── pyproject.toml      # Poetry dependencies
├── mcp-server/             # MCP tool server
│   ├── src/
│   │   ├── tools/          # MCP tool definitions
│   │   ├── api_client.py   # FastAPI client wrapper
│   │   └── server.py       # MCP server entry
│   └── pyproject.toml
├── frontend/               # React Web UI
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Route pages
│   │   ├── services/       # API client
│   │   └── main.tsx        # Vite entry
│   ├── tests/              # Frontend tests
│   └── package.json
└── specs/                  # Specifications & plans
```

---

## Step 1: Database Setup

### 1.1 Create PostgreSQL Database

```bash
# Start PostgreSQL service (macOS with Homebrew)
brew services start postgresql@15

# Create database and user
psql postgres -c "CREATE USER ras_hunter WITH PASSWORD 'dev_password';"
psql postgres -c "CREATE DATABASE ras_hunter OWNER ras_hunter;"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE ras_hunter TO ras_hunter;"
```

### 1.2 Initialize Schema

Navigate to backend directory and run migrations:

```bash
cd backend
poetry install  # Install dependencies (includes alembic)
poetry run alembic upgrade head  # Apply migrations
```

**Expected output**: `Running upgrade -> abc123, create initial schema`

### 1.3 Seed Test Data (Optional)

```bash
poetry run python scripts/seed_test_data.py
```

This creates:
- 3 test users: `alice`, `bob`, `charlie` (password: `testpass123`)
- 1 active match with 20 submarines
- Sample map with treasure at (15, 20)

---

## Step 2: Redis Setup

### 2.1 Start Redis Server

```bash
# Start Redis service (macOS with Homebrew)
brew services start redis

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

### 2.2 Configure Cache

Redis runs on default port `6379`. No additional configuration needed for development.

---

## Step 3: Backend Setup

### 3.1 Install Dependencies

```bash
cd backend
poetry install
```

### 3.2 Configure Environment

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://ras_hunter:dev_password@localhost:5432/ras_hunter

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
JWT_SECRET=your-secret-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# OpenTelemetry (optional, requires Docker)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_SERVICE_NAME=ras-hunter-backend
OTEL_TRACES_ENABLED=false  # Set to true after starting Jaeger
```

### 3.3 Run Development Server

```bash
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete
```

**Test API health**:
```bash
curl http://localhost:8000/api/health
# Response: {"status": "ok", "database": "connected", "redis": "connected"}
```

**View OpenAPI docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Step 4: MCP Server Setup

### 4.1 Install Dependencies

```bash
cd mcp-server
poetry install
```

### 4.2 Configure Environment

Create `.env` file in `mcp-server/` directory:

```env
# FastAPI Backend URL
BACKEND_URL=http://localhost:8000

# MCP Server
MCP_PORT=3000
LOG_LEVEL=INFO
```

### 4.3 Run MCP Server

```bash
poetry run python src/server.py
```

**Expected output**:
```
INFO:     MCP server listening on http://localhost:3000
INFO:     Available tools: discover, surface, use_tool, exchange_frequency, broadcast, direct_message
INFO:     Backend health check: OK
```

**Test MCP tool** (requires Claude Desktop or compatible MCP client):
```json
{
  "tool": "discover",
  "arguments": {
    "token": "your-jwt-token",
    "x": 5,
    "y": 7
  }
}
```

---

## Step 5: Frontend Setup

### 5.1 Install Dependencies

```bash
cd frontend
npm install
```

### 5.2 Configure Environment

Create `.env.local` file in `frontend/` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

### 5.3 Run Development Server

```bash
npm run dev
```

**Expected output**:
```
VITE v5.0.0  ready in 423 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

**Access Web UI**: [http://localhost:5173](http://localhost:5173)

---

## Step 6: Run Tests

### 6.1 Backend Tests

```bash
cd backend
poetry run pytest tests/ -v --cov=src
```

**Expected output**: E2E tests for authentication, game actions, communication, observability.

### 6.2 Frontend Tests

```bash
cd frontend
npm test  # Jest unit tests
npm run test:e2e  # Playwright E2E tests
```

### 6.3 Integration Tests

```bash
cd backend
poetry run pytest tests/integration/ -v
```

Tests full game flow:
1. Register 20 players
2. Start match
3. Player discovers tiles, uses tools, exchanges frequencies
4. Player finds treasure, surfaces at home_base
5. Verify match ends with correct winner

---

## Step 7: Observability Stack (Optional)

### 7.1 Start Jaeger, Prometheus, Grafana

```bash
cd observability
docker-compose up -d
```

**Services**:
- Jaeger UI: [http://localhost:16686](http://localhost:16686) (distributed tracing)
- Prometheus: [http://localhost:9090](http://localhost:9090) (metrics)
- Grafana: [http://localhost:3001](http://localhost:3001) (dashboards, login: admin/admin)

### 7.2 Enable Tracing in Backend

Update `backend/.env`:
```env
OTEL_TRACES_ENABLED=true
OTEL_METRICS_ENABLED=true
```

Restart backend:
```bash
cd backend
poetry run uvicorn src.main:app --reload
```

### 7.3 View Traces

1. Open Jaeger UI: [http://localhost:16686](http://localhost:16686)
2. Select service: `ras-hunter-backend`
3. Click "Find Traces"
4. View trace details: HTTP requests, database queries, Redis operations

### 7.4 View Metrics

1. Open Grafana: [http://localhost:3001](http://localhost:3001) (admin/admin)
2. Add Prometheus datasource: `http://prometheus:9090`
3. Import dashboard from `observability/grafana-dashboard.json`
4. View metrics: request latency, active players, oxygen distribution, EMP hits

---

## Step 8: Play the Game

### 8.1 Register Users

Open Web UI: [http://localhost:5173](http://localhost:5173)

1. Click "Register"
2. Username: `test_player_1` (3-20 chars, alphanumeric + underscore)
3. Password: `testpass123` (min 8 chars)
4. Click "Create Account"

Repeat for 19 more players (or use seed script from Step 1.3).

### 8.2 Start Match

1. Login as `test_player_1`
2. Click "Join Match" (auto-creates match if none active)
3. Wait for 20 players to join (or click "Start Match" if seeded)

### 8.3 Explore Map

1. **Discover**: Click adjacent tile (4-neighbor) to reveal content
   - Costs 1 oxygen per discovery
   - 8-second cooldown
2. **Use Tool**: If tile contains tool, pick it up and use:
   - **EMP**: Disable adjacent submarine for 30s
   - **Sonar**: Reveal 7×7 area around you
   - **Repair Kit**: Restore oxygen to 20, clear EMP hits
3. **Surface**: Click "Surface" button to restore oxygen (60s duration)
4. **Exchange Frequency**: Click adjacent submarine to swap frequencies (enables direct messaging)

### 8.4 Find Treasure

1. Discover treasure tile (marked as "★" on map)
2. Walk onto treasure tile to pick up
3. Return to your home_base (marked as "H")
4. Surface at home_base while holding treasure
5. **You win!** Match ends, leaderboard shows standings

### 8.5 Use MCP Tools (AI Agents)

Open Claude Desktop (or compatible MCP client):

1. Configure MCP server:
   ```json
   {
     "mcpServers": {
       "ras-hunter": {
         "url": "http://localhost:3000"
       }
     }
   }
   ```
2. Authenticate: "Use `ras_hunter_login` tool with username and password"
3. Explore: "Use `ras_hunter_discover` to explore tile at (5, 7)"
4. Strategy: "Use `ras_hunter_game_state` to see treasure holder and leaderboard"

---

## Troubleshooting

### Database Connection Errors

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
```bash
# Check PostgreSQL status
brew services list | grep postgresql

# Start if not running
brew services start postgresql@15

# Verify connection
psql -U ras_hunter -d ras_hunter -c "SELECT 1;"
```

### Redis Connection Errors

**Error**: `redis.exceptions.ConnectionError: Error connecting to localhost:6379`

**Solution**:
```bash
# Check Redis status
brew services list | grep redis

# Start if not running
brew services start redis

# Verify connection
redis-cli ping
```

### Port Conflicts

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port in backend/.env
PORT=8001
```

### JWT Token Expired

**Error**: `401 Unauthorized: JWT token is expired`

**Solution**: Login again to get new token (24-hour expiry).

---

## Next Steps

- **Implement Game Logic**: Follow `specs/001-deep-treasure-game/plan.md` task breakdown
- **Add Random Events**: Implement leaks, pressure spikes per FR-041, FR-042
- **Deploy to Production**: See deployment guide in `docs/deployment.md`
- **Scale to 100 Players**: Optimize database queries, add Redis cluster

---

## Useful Commands

| Task | Command |
|------|---------|
| Run all tests | `make test` (from project root) |
| Format code | `poetry run black . && poetry run isort .` (backend) |
| Lint code | `poetry run ruff check .` (backend) |
| Type check | `poetry run mypy src/` (backend) |
| Generate migration | `poetry run alembic revision --autogenerate -m "description"` |
| Reset database | `poetry run alembic downgrade base && alembic upgrade head` |
| Tail logs | `docker-compose logs -f` (observability stack) |
| Clear Redis | `redis-cli FLUSHALL` |

---

## Support

- **Specification**: `specs/001-deep-treasure-game/spec.md`
- **Implementation Plan**: `specs/001-deep-treasure-game/plan.md`
- **Data Model**: `specs/001-deep-treasure-game/data-model.md`
- **API Contracts**: `specs/001-deep-treasure-game/contracts/openapi.yaml`
- **Constitution**: `.specify/memory/constitution.md`

**Happy treasure hunting! 🚢💎**
