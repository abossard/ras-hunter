# Research: Ras's Deep Treasure Game

**Phase**: 0 (Outline & Research)
**Date**: 2025-10-24
**Status**: Complete

## Decision Summary

All technical unknowns resolved. No NEEDS CLARIFICATION items remain from Technical Context section.

---

## 1. Backend Framework: FastAPI vs Flask vs Django

**Decision**: FastAPI

**Rationale**:
- **Async Support**: Native async/await for WebSocket connections and concurrent 20-player request handling without blocking
- **OpenAPI Integration**: Automatic OpenAPI schema generation from route decorators; eliminates manual contract maintenance
- **Type Safety**: Pydantic models for request/response validation; catches type errors at startup
- **Performance**: ASGI server (Uvicorn) outperforms WSGI (Flask/Django) for I/O-bound workloads (database + cache + WebSocket)
- **Simplicity**: Less framework ceremony than Django; more structure than Flask

**Alternatives Considered**:
- **Django REST Framework**: Full-featured but heavyweight (ORM, admin, migrations coupled); violates Simplicity principle for this scope
- **Flask**: Minimal but requires manual OpenAPI tooling (flask-swagger) and lacks native async support
- **Node.js (Express/NestJS)**: Cross-language complexity (Python for MCP server); Python has better PostgreSQL/Redis ecosystem

---

## 2. Database: PostgreSQL vs MongoDB vs SQLite

**Decision**: PostgreSQL 15+

**Rationale**:
- **ACID Guarantees**: Critical for match state consistency (treasure pickup, EMP hits, victory conditions) under concurrent writes
- **JSON Support**: `JSONB` columns for flexible schema storage (known_fields map, travel_log array) without sacrificing relational integrity
- **Performance**: Mature query planner for complex joins (match + submarines + messages); supports indexes on JSONB fields
- **Ecosystem**: Excellent Python support (psycopg3, SQLAlchemy ORM); proven at scale

**Alternatives Considered**:
- **MongoDB**: Schema flexibility unnecessary (entities well-defined in spec); lacks ACID transactions across documents (pre-4.0) or requires sharding complexity
- **SQLite**: Insufficient for 20 concurrent writers (file-level locking); no network access for distributed deployment
- **MySQL**: PostgreSQL's JSONB and CTEs (Common Table Expressions) more powerful for nested data queries

---

## 3. Cache Layer: Redis vs Memcached vs In-Process

**Decision**: Redis 7+

**Rationale**:
- **Data Structures**: Native support for maps (HSET for submarine state), lists (LPUSH for message queues), sorted sets (ZADD for leaderboard)
- **Persistence**: Optional AOF (Append-Only File) for cache warmup after Redis restart; balances speed with durability
- **Pub/Sub**: Built-in publish/subscribe for WebSocket event broadcasting (treasure discovered, EMP hit)
- **Atomic Operations**: INCR, DECR for oxygen/discovery counters without race conditions
- **Single-Threaded Model**: Simplifies reasoning about concurrent operations (no lock contention)

**Alternatives Considered**:
- **Memcached**: Key-value only (no maps/lists); no persistence; no pub/sub
- **In-Process Cache (lru_cache)**: Lost on server restart; not shared across FastAPI worker processes
- **Hazelcast/Coherence**: Enterprise complexity unjustified for 20-player scale

---

## 4. Authentication: JWT vs Session Tokens vs OAuth2

**Decision**: JWT (JSON Web Tokens) with 24-hour expiry

**Rationale**:
- **Stateless**: No server-side session storage; scales horizontally without sticky sessions or shared session store
- **Payload**: Embed `username`, `sub_id`, `exp` (expiry) in token; avoid database lookup per request
- **Standard**: RFC 7519; libraries mature (PyJWT for Python, jsonwebtoken for Node.js)
- **MCP Compatibility**: Token passed in MCP tool metadata (`Authorization: Bearer <token>`); no cookies required

**Alternatives Considered**:
- **Session Tokens (Opaque)**: Requires server-side session store (Redis or database); adds latency and complexity
- **OAuth2**: Over-engineered for simple username/password; third-party provider (Google/GitHub) out of scope per spec assumption

---

## 5. WebSocket Library: Socket.IO vs Native WebSocket vs Server-Sent Events

**Decision**: Native WebSocket (FastAPI + Starlette WebSocketEndpoint)

**Rationale**:
- **Simplicity**: No additional library (Socket.IO) needed; FastAPI has native WebSocket support via Starlette
- **Bidirectional**: Enables server→client broadcasts (treasure discovered) and client→server actions (via same connection or separate REST calls)
- **Fallback**: Spec allows 5-second polling fallback; no need for Socket.IO's transport negotiation complexity

**Alternatives Considered**:
- **Socket.IO**: Auto-reconnect and fallback built-in, but adds protocol overhead and client library dependency
- **Server-Sent Events (SSE)**: Server→client only; requires separate HTTP for client→server actions; less efficient for bidirectional

---

## 6. Frontend Framework: React vs Vue vs Svelte

**Decision**: React 18+ with TypeScript

**Rationale**:
- **Ecosystem**: Largest component library ecosystem (Material-UI, Ant Design); more third-party integrations (OpenTelemetry browser SDK, WebSocket hooks)
- **TypeScript Integration**: First-class support; type-safe props and state
- **Hooks**: useEffect for polling, useWebSocket (custom hook) for real-time updates
- **Testing**: React Testing Library + Jest mature; Playwright E2E tests work well with React

**Alternatives Considered**:
- **Vue 3**: Simpler API but smaller ecosystem; less familiar to AI agent developers (MCP focus)
- **Svelte**: Compile-time optimization appealing, but newer ecosystem; fewer component libraries

---

## 7. MCP Server Implementation: Custom vs mcp-framework

**Decision**: Use MCP SDK (official Python library)

**Rationale**:
- **Protocol Compliance**: Ensures correct JSON-RPC 2.0 message format per MCP spec
- **Tool Registry**: Automatic tool discovery and schema validation
- **Error Handling**: Standardized error codes and message formats
- **Maintenance**: Official SDK receives protocol updates from Anthropic

**Alternatives Considered**:
- **Custom JSON-RPC Server**: Risk of protocol drift; manual schema validation; violates Simplicity principle (reinventing MCP SDK)

---

## 8. OpenTelemetry Backend: Jaeger vs Prometheus+Grafana vs DataDog

**Decision**: Jaeger (traces) + Prometheus (metrics) + Grafana (visualization)

**Rationale**:
- **Open Source**: No vendor lock-in; full control over data retention
- **OTLP Support**: Both accept OpenTelemetry Protocol exports (traces, metrics, logs)
- **Deployment**: Docker Compose for local dev; Kubernetes Helm charts for production
- **Cost**: Free for self-hosted; DataDog/Honeycomb enterprise pricing unjustified for 20-player game

**Alternatives Considered**:
- **DataDog/New Relic**: SaaS ease-of-use but high cost at scale; unnecessary for this scope
- **Elastic APM**: Heavier (Elasticsearch cluster); overkill for 20 concurrent players

---

## 9. Password Hashing: bcrypt vs argon2 vs scrypt

**Decision**: bcrypt (via `bcrypt` Python library)

**Rationale**:
- **Battle-Tested**: 20+ years in production; known security properties
- **Work Factor**: Tunable cost parameter (default 12 rounds) balances security vs latency
- **Python Support**: Native C bindings (`bcrypt` package); fast and audited
- **Sufficient**: No quantum resistance needed for game authentication (not financial/gov)

**Alternatives Considered**:
- **argon2**: Winner of Password Hashing Competition (2015); slightly better GPU resistance, but bcrypt sufficient for this threat model
- **PBKDF2**: No adaptive work factor (fixed iterations); vulnerable to hardware acceleration

---

## 10. Game State Concurrency: Optimistic Locking vs Pessimistic Locking vs Event Sourcing

**Decision**: Optimistic Locking with Timestamp Ordering

**Rationale**:
- **Spec Alignment**: FR-043 mandates "timestamp first-come, ties by sub_id"; optimistic locking fits naturally
- **Conflict Resolution**: Compare action timestamp; reject stale actions (e.g., simultaneous treasure discovery)
- **Performance**: No database row locks held; higher throughput for independent actions (different tiles)
- **Simplicity**: Less complex than event sourcing (no event replay logic); easier to debug

**Alternatives Considered**:
- **Pessimistic Locking**: `SELECT ... FOR UPDATE` blocks concurrent reads; degrades performance for independent actions
- **Event Sourcing**: Full audit log appealing for time-travel debugging, but adds complexity (event replay, projections); violates Simplicity unless justified by specific undo/replay features

---

## 11. Map Tile Storage: Relational Table vs JSONB Column vs In-Memory Only

**Decision**: Hybrid - Initial Map in JSONB, Discovered Tiles in Relational Table

**Rationale**:
- **Initial Map**: Store full 32×32 tile content as JSONB in `matches.map_configuration` (1024 entries, ~50KB); generated once per match
- **Discovered Tiles**: Separate `discovered_tiles` table with `(match_id, sub_id, x, y, discovered_at)` for query efficiency (e.g., "which tiles has sub-01 discovered?")
- **Trade-off**: JSONB allows fast full-map load; relational table enables indexed queries per player

**Alternatives Considered**:
- **Pure Relational**: 1024 rows per match in `tiles` table; more normalized but slower initial map generation
- **Pure JSONB**: All state in one column; harder to query "all players who discovered tile (5,7)"

---

## 12. Real-Time Update Strategy: Polling vs WebSocket vs Long-Polling

**Decision**: WebSocket Primary, 5-Second Polling Fallback

**Rationale**:
- **Spec Mandate**: FR-052 and FR-060 specify WebSocket with polling fallback
- **Latency**: WebSocket push events (treasure discovered, EMP hit) arrive instantly vs 5s polling delay
- **Efficiency**: Single persistent connection vs repeated HTTP requests (reduced overhead for 20 players)
- **Fallback**: Polling handles restrictive corporate firewalls or proxy issues

**Alternatives Considered**:
- **Pure Polling**: Simpler implementation but 5s latency for all events; violates SC-003 (1s treasure broadcast requirement)
- **Long-Polling (Comet)**: Holds connection open until event; more complex than WebSocket, similar firewall issues

---

## Research Artifacts

No external research artifacts generated (all decisions based on existing best practices and spec requirements).

## Next Steps

Proceed to **Phase 1: Design & Contracts** to generate:
1. `data-model.md` (entity schemas with fields, relationships, constraints)
2. `contracts/openapi.yaml` (REST API endpoint definitions)
3. `quickstart.md` (local setup and run instructions)
