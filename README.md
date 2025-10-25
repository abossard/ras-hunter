# Ras's Deep Treasure 🌊💎

A multiplayer submarine treasure hunt game with fog-of-war exploration, oxygen management, EMP combat, and frequency-based communication.

## 🎮 Game Overview

20 players compete in submarines to find the **one treasure** on a 32×32 grid. Navigate through fog-of-war, manage oxygen carefully, discover tiles (empty, tool, or hazard), communicate via radio frequencies, and use EMP blasts to eliminate competitors.

**Features:**
- 🗺️ **Fog-of-War Exploration**: Discover adjacent tiles to reveal the map
- 💨 **Oxygen Management**: Deplete oxygen with actions, surface to recharge
- 🔧 **Tool Discovery**: Find speed, vision, and shield enhancements
- ⚡ **EMP Combat**: Eliminate submarines within 2 tiles
- 📻 **Frequency Communication**: Share secrets or deceive using shared channels
- 🏆 **Winner Takes All**: First to capture the treasure wins

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Start all services (backend, frontend, database, observability)
docker-compose up -d --build

# Check service health
docker-compose ps

# View logs
docker-compose logs -f backend

# Access the application
# - Frontend: http://localhost:5173
# - API Docs: http://localhost:8000/docs
# - Jaeger UI: http://localhost:16686
# - Grafana: http://localhost:3001 (admin/admin)

# Stop services
docker-compose down
```

📖 See [DOCKER.md](./DOCKER.md) for complete Docker setup guide.

### Manual Setup (Development)

**Prerequisites:**
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

**Backend:**
```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**MCP Server:**
```bash
cd mcp-server
poetry install
poetry run python -m src.server
```

## 📁 Project Structure

```
ras-hunter/
├── backend/              # FastAPI REST API + WebSocket server
│   ├── src/
│   │   ├── models/      # SQLAlchemy database models
│   │   ├── services/    # Business logic
│   │   ├── api/         # API endpoints
│   │   ├── cache/       # Redis client
│   │   └── observability/ # OpenTelemetry
│   ├── tests/           # Backend tests
│   └── alembic/         # Database migrations
├── mcp-server/          # Model Context Protocol server (AI agents)
│   └── src/tools/       # MCP tools wrapping API
├── frontend/            # React + TypeScript web UI
│   └── src/
│       ├── components/  # React components
│       ├── pages/       # Page components
│       └── services/    # API client
├── tests/e2e/           # Playwright end-to-end tests
├── observability/       # Monitoring stack (Jaeger, Prometheus, Grafana)
└── specs/               # Feature specifications
    └── 001-deep-treasure-game/
        ├── spec.md      # Feature specification
        ├── plan.md      # Implementation plan
        ├── tasks.md     # Task breakdown
        └── contracts/   # API contracts (OpenAPI)
```

## 🛠️ Technology Stack

**Backend:**
- FastAPI (async REST API)
- SQLAlchemy 2.0+ (async ORM)
- PostgreSQL 15+ (database)
- Redis 7+ (cache + pub/sub)
- JWT authentication
- OpenTelemetry (observability)

**Frontend:**
- React 18
- TypeScript
- Vite (bundler)
- Axios (HTTP client)

**MCP Server:**
- Model Context Protocol SDK
- Wraps backend API for AI agent access

**Testing:**
- pytest (backend)
- Playwright (E2E)
- Contract tests (OpenAPI compliance)

## 📊 API Documentation

Interactive API documentation available when backend is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 Testing

```bash
# Backend unit tests
cd backend
poetry run pytest tests/unit/

# Backend integration tests
poetry run pytest tests/integration/

# Contract tests
poetry run pytest tests/contract/

# E2E tests (requires running services)
cd tests/e2e
npm install
npm run test
```

## 📈 Monitoring & Observability

The stack includes comprehensive observability:

**Distributed Tracing (Jaeger):**
- URL: http://localhost:16686
- Trace discovery, surface, and combat operations
- Analyze latency and service dependencies

**Metrics (Prometheus + Grafana):**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- Track active players, actions/min, API latency

**Structured Logging:**
- JSON format with trace_id injection
- Correlation across distributed traces

## 🎯 Development Workflow

1. **Specification Phase**: See `specs/001-deep-treasure-game/spec.md`
2. **Implementation Plan**: See `specs/001-deep-treasure-game/plan.md`
3. **Task Breakdown**: See `specs/001-deep-treasure-game/tasks.md`
4. **Implementation**: Tasks organized by user story (independent, parallel)

**Constitution Principles:**
1. ✨ **Simplicity**: Small focused functions, clear data flow
2. 📝 **Explicitness**: Typed APIs, validated inputs, documented decisions
3. 🧪 **High-Value Tests**: E2E + Contract > Unit tests
4. 🔍 **Diagnostic Errors**: Structured errors with error_code + diagnostic context
5. 🌱 **Incremental Evolution**: MVP-first, feature flags, backward compatibility

## 🏗️ Implementation Status

**✅ Complete:**
- Phase 1: Project setup (10/10 tasks)
- Phase 2: Foundation (12/12 backend tasks)
  - Configuration, database, Redis, auth, observability
  - FastAPI app with CORS, error handlers, health checks

**🔄 In Progress:**
- Phase 3: User Story 1 - Solo Exploration (36 tasks)
  - Database models, services, API endpoints
  - Frontend UI components

**⏳ Pending:**
- Phase 4-11: Multiplayer features (138 tasks)
  - Matchmaking, combat, communication, events

## 🤝 Contributing

1. Follow constitution principles (see `specs/001-deep-treasure-game/constitution.md`)
2. Write tests before implementation (TDD encouraged)
3. Use task breakdown in `specs/001-deep-treasure-game/tasks.md`
4. Ensure API contracts match `specs/001-deep-treasure-game/contracts/`

## 📝 License

See LICENSE file for details.

## 🔗 Links

- **Specifications**: `specs/001-deep-treasure-game/`
- **API Contracts**: `specs/001-deep-treasure-game/contracts/openapi.yaml`
- **Quick Start Guide**: `specs/001-deep-treasure-game/quickstart.md`
- **Docker Guide**: [DOCKER.md](./DOCKER.md)

---

Built with ❤️ using Spec-Driven Development
