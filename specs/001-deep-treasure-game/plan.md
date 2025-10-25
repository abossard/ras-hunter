# Implementation Plan: Ras's Deep Treasure Game

**Branch**: `001-deep-treasure-game` | **Date**: 2025-10-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-deep-treasure-game/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Multiplayer submarine treasure hunt game supporting 20 concurrent players via Web UI (human players) and MCP tools (AI agents). Players explore a fog-of-war 32×32 ocean grid, manage oxygen resources, discover tools/hazards, and race to find treasure and return to home base. Features include EMP combat, frequency-based communication, persistent database storage with in-memory caching, and full OpenTelemetry observability. Technical approach: Python backend (FastAPI) with PostgreSQL + Redis, React frontend, MCP server wrapping REST API, OpenAPI contracts, and WebSocket for real-time events.

## Technical Context

**Language/Version**: Python 3.11+ (backend/MCP server), TypeScript/JavaScript (frontend)
**Primary Dependencies**: FastAPI (REST API), MCP SDK (Model Context Protocol server), PostgreSQL (persistent storage), Redis (in-memory cache), React (Web UI), OpenTelemetry SDK (observability), WebSocket (real-time updates), bcrypt (password hashing), JWT/session tokens (authentication)
**Storage**: PostgreSQL (user accounts, match state, submarine data, historical matches), Redis (active match cache for low-latency reads)
**Testing**: pytest (backend unit/integration/contract tests), Jest + React Testing Library (frontend), Playwright (E2E tests), OpenAPI contract validation
**Target Platform**: Linux server (backend/MCP), modern browsers (Chrome/Firefox/Safari for Web UI)
**Project Type**: Web application (frontend + backend + MCP server)
**Performance Goals**: 10s ± 0.5s discovery action latency (95%ile), <2s Web UI load time, <50ms OpenTelemetry instrumentation overhead, 20 concurrent players without degradation
**Constraints**: Hard cap 20 players per match, 10-minute inactivity timeout, synchronous database flush for critical events (treasure pickup, victory, EMP hits), 4-neighbor movement only (no diagonals)
**Scale/Scope**: 20 concurrent players max, 32×32 map grid (1024 tiles), ~50-100 actions per player per match, persistent historical match storage

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Project MUST satisfy all current ras-hunter Constitution gates:

- Simplicity: New dependency or abstraction documented with justification (benefit > cost).
- Explicitness: Each new module/function documents inputs/outputs/side-effects (docstring or README snippet).
- E2E & Contract Coverage: Planned user journeys and any external contract changes have a corresponding planned E2E or contract test.
- Diagnostic Errors: Planned features specify primary failure modes and contextual data to surface.
- Evolution Safety: Any anticipated breaking change has a migration outline + proposed version impact.

Failure to meet any gate: STOP and revise plan before implementation.

## Project Structure

### Documentation (this feature)

```text
specs/001-deep-treasure-game/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── openapi.yaml     # OpenAPI 3.0 schema for REST endpoints
├── checklists/
│   └── requirements.md  # Quality validation checklist
└── spec.md              # Feature specification
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # SQLAlchemy ORM models (User, Match, Submarine, Tile, Message, Event)
│   ├── services/        # Business logic (game engine, match manager, submarine controller, combat, communication)
│   ├── api/             # FastAPI routes (auth, game actions, query endpoints)
│   ├── cache/           # Redis cache layer (read-through, write-through patterns)
│   ├── observability/   # OpenTelemetry setup (tracing, metrics, logging)
│   ├── config.py        # Configuration (database URL, Redis URL, JWT secret, map size)
│   └── main.py          # FastAPI app entry point
├── tests/
│   ├── contract/        # OpenAPI contract validation tests
│   ├── integration/     # Multi-component tests (API + database + cache)
│   └── unit/            # Pure logic tests (game rules, combat calculations, oxygen management)
├── pyproject.toml       # Poetry dependency management
└── Dockerfile           # Container image for backend

mcp-server/
├── src/
│   ├── tools/           # MCP tool implementations (discover, surface, use_tool, etc.)
│   ├── api_client.py    # HTTP client wrapping backend REST API
│   └── server.py        # MCP server entry point
├── tests/
│   └── integration/     # MCP tool → API integration tests
└── pyproject.toml       # MCP SDK dependencies

frontend/
├── src/
│   ├── components/      # React components (MapGrid, StatusPanel, CommsPanel, Leaderboard, ReplayTimeline)
│   ├── pages/           # Route pages (Login, Register, Game, Replay)
│   ├── services/        # API client, WebSocket client
│   ├── hooks/           # Custom React hooks (useGameState, useWebSocket, useAuth)
│   └── App.tsx          # Main app component
├── tests/
│   ├── unit/            # Component unit tests
│   └── integration/     # API integration tests
├── package.json
└── vite.config.ts       # Vite bundler config

tests/
└── e2e/                 # Playwright E2E tests (login → spawn → discover → treasure → victory)
```

**Structure Decision**: Web application architecture selected due to requirements for both Web UI (human players) and MCP tools (AI agents) accessing the same backend. Backend and mcp-server both target Python 3.11+ for consistency, enabling code reuse for shared logic (authentication, data models). Frontend uses React + TypeScript for modern UI patterns and type safety. Separation allows independent deployment and scaling of backend API, MCP server, and frontend static assets.

## Complexity Tracking

✅ **No violations** - Constitution gates satisfied:

- **Simplicity**: Dependencies justified by requirements (FastAPI for REST API simplicity vs Django overhead; PostgreSQL for ACID guarantees; Redis for sub-10ms cache reads; MCP SDK for AI agent protocol compliance; OpenTelemetry for production debugging at 20-player concurrency scale)
- **Explicitness**: All modules document inputs/outputs (OpenAPI spec for API, type hints in Python, TypeScript interfaces in frontend, MCP tool schemas)
- **E2E & Contract Coverage**: Test plan includes E2E (login → treasure → victory), contract tests (OpenAPI validation), selective unit tests (game rules, oxygen calculations)
- **Diagnostic Errors**: FR-045 and FR-052 specify error context requirements (error_code, operation_name, submarine_id, trace_id, expected vs actual)
- **Evolution Safety**: OpenAPI versioning enables backward-compatible API evolution; database migrations planned

---

## Phase 0: Research & Planning

**Status**: ✅ Complete

Phase 0 artifacts:
- ✅ **`research.md`**: 12 technical decisions documented with rationale and alternatives
  - Backend: FastAPI (async, OpenAPI generation, type safety)
  - Database: PostgreSQL 15+ (ACID, JSONB support)
  - Cache: Redis 7+ (data structures, pub/sub)
  - Auth: JWT (stateless, 24-hour expiry)
  - Real-time: Native WebSocket + polling fallback
  - Frontend: React 18+ with TypeScript
  - MCP: Official MCP SDK (protocol compliance)
  - Observability: Jaeger + Prometheus + Grafana
  - Security: bcrypt password hashing (work factor 12)
  - Concurrency: Optimistic locking with timestamp ordering
  - Map Storage: Hybrid JSONB + relational
  - Communication: WebSocket primary, polling fallback

---

## Phase 1: Design Artifacts

**Status**: ✅ Complete

Phase 1 artifacts:
- ✅ **`data-model.md`**: Entity schemas (User, Match, Submarine, Message, Event) with fields, relationships, validation rules, state transitions, indexes
- ✅ **`contracts/openapi.yaml`**: REST API endpoint definitions (13 endpoints: authentication, game actions, communication, information queries) with OpenAPI 3.1.0 specification
- ✅ **`quickstart.md`**: Local development setup (8 steps: prerequisites, database, Redis, backend, MCP server, frontend, tests, observability)

Key Design Decisions:
- **3-Component Architecture**: backend (FastAPI), mcp-server (MCP SDK), frontend (React)
- **Authentication Flow**: POST /api/register → POST /api/login (JWT bearer token, 24h expiry)
- **Game Actions**: discover (4-neighbor, 8s cooldown), surface (60s duration), use_tool (EMP/sonar/repair_kit), exchange_frequency
- **Communication**: broadcast (to "ALL") and direct (via exchanged frequencies)
- **Observability**: OpenTelemetry traces, metrics, logs exported to Jaeger/Prometheus
- **State Management**: PostgreSQL for persistence, Redis for hot cache with write-through pattern
- **Error Handling**: Diagnostic error_code + context object per FR-052

---

## Implementation Status

**Planning Phase**: ✅ Complete (Phase 0 + Phase 1)

**Next Steps**:
1. Run `/speckit.tasks` command to generate task breakdown (Phase 2)
2. Review tasks and assign to developers
3. Begin implementation following constitution principles
4. Execute E2E tests after each user story completes
5. Deploy to staging environment for integration testing

**Commit Suggestion**:
```bash
git add specs/001-deep-treasure-game/
git commit -m "docs: complete implementation plan for 001-deep-treasure-game (Phase 0-1)

- Add research.md with 12 technical decisions
- Add data-model.md with 5 entity schemas
- Add contracts/openapi.yaml with 13 REST endpoints
- Add quickstart.md with 8-step local setup
- Constitution check passed: all gates satisfied
- Ready for Phase 2 task breakdown via /speckit.tasks"
```

---

**Planning Complete**: This document, along with `research.md`, `data-model.md`, `contracts/openapi.yaml`, and `quickstart.md`, provides the technical foundation for implementing the Ras's Deep Treasure game. Proceed to Phase 2 (task breakdown) using the `/speckit.tasks` command.

