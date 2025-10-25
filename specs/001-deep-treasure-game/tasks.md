# Tasks: Ras's Deep Treasure Game

**Input**: Design documents from `/specs/001-deep-treasure-game/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/openapi.yaml ✅

**Tests**: Prioritize high-value End-to-End (user journey) and Contract tests (public interfaces). Add focused unit tests ONLY for complex pure logic. Tests are OPTIONAL unless mandated by specification or required to cover a new external contract.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md, this is a web application with 3 main components:
- **Backend**: `backend/src/`, `backend/tests/`
- **MCP Server**: `mcp-server/src/`, `mcp-server/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **E2E Tests**: `tests/e2e/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure: backend/src/{models,services,api,cache,observability}, backend/tests/{unit,integration,contract}
- [X] T002 Initialize backend Python project with Poetry in backend/pyproject.toml (dependencies: fastapi, sqlalchemy, psycopg2-binary, redis, pydantic, python-jose, passlib, opentelemetry-api, opentelemetry-sdk, opentelemetry-instrumentation-fastapi)
- [X] T003 [P] Create mcp-server directory structure: mcp-server/src/{tools}, mcp-server/tests/integration
- [X] T004 [P] Initialize mcp-server Python project with Poetry in mcp-server/pyproject.toml (dependencies: mcp, httpx, pydantic)
- [X] T005 [P] Create frontend directory structure: frontend/src/{components,pages,services,hooks}, frontend/tests/{unit,integration}
- [X] T006 [P] Initialize frontend React+TypeScript project with Vite in frontend/package.json (dependencies: react, react-dom, typescript, vite, axios, react-router-dom)
- [X] T007 [P] Create E2E test directory: tests/e2e/ and initialize Playwright in tests/e2e/package.json
- [X] T008 [P] Configure linting and formatting: backend/.ruff.toml, backend/.mypy.ini, frontend/.eslintrc.json, frontend/.prettierrc
- [X] T009 [P] Create backend Dockerfile in backend/Dockerfile (Python 3.11 base, poetry install, uvicorn CMD)
- [X] T010 [P] Create observability docker-compose.yaml in observability/docker-compose.yaml (Jaeger, Prometheus, Grafana services)
- [X] T010a [P] Create root docker-compose.yml orchestrating all services (backend, mcp-server, frontend, postgres, redis, observability stack) with health checks and dependencies
- [X] T010b [P] Create MCP server Dockerfile in mcp-server/Dockerfile (Python 3.11 base, poetry install)
- [X] T010c [P] Create frontend Dockerfile in frontend/Dockerfile (Node 20 alpine, multi-stage build with nginx)
- [X] T010d [P] Create DOCKER.md with complete docker-compose guide, troubleshooting, monitoring setup
- [X] T010e [P] Create Makefile with convenient commands (make up, make down, make test, make logs, etc.)
- [X] T010f [P] Create .env.example template with all environment variables documented

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 Create database configuration in backend/src/config.py (DATABASE_URL, REDIS_URL, JWT_SECRET, MAP_SIZE env vars)
- [X] T012 Setup SQLAlchemy engine and session factory in backend/src/database.py (async engine, session maker, Base declarative)
- [X] T013 Create Alembic configuration in backend/alembic.ini and backend/alembic/env.py for database migrations
- [X] T014 [P] Create Redis client singleton in backend/src/cache/redis_client.py (connection pool, get/set/delete/publish helpers)
- [X] T015 [P] Implement JWT authentication utilities in backend/src/services/auth_service.py (create_token, verify_token, get_current_user dependency)
- [X] T016 [P] Implement password hashing utilities in backend/src/services/password_service.py (hash_password with bcrypt work factor 12, verify_password)
- [X] T017 [P] Setup OpenTelemetry instrumentation in backend/src/observability/tracer.py (TracerProvider, OTLP exporter, FastAPI instrumentation)
- [X] T018 [P] Setup OpenTelemetry metrics in backend/src/observability/metrics.py (MeterProvider, counters for actions, histograms for latency)
- [X] T019 [P] Setup structured logging in backend/src/observability/logger.py (JSON formatter, trace_id injection, log levels)
- [X] T020 Create base error handlers in backend/src/api/error_handlers.py (HTTPException to Error schema with error_code and context per FR-052)
- [X] T021 Create FastAPI app initialization in backend/src/main.py (app instance, CORS middleware, OpenTelemetry middleware, error handlers, lifespan context)
- [X] T022 Create initial Alembic migration for base schema in backend/alembic/versions/001_initial_schema.py (empty, will be populated by entity migrations)
- [ ] T023 [P] Create API client base in frontend/src/services/api-client.ts (axios instance, bearer token interceptor, error handling)
- [ ] T024 [P] Create WebSocket client in frontend/src/services/websocket-client.ts (connection manager, message handler, reconnection logic)
- [ ] T025 [P] Create authentication context in frontend/src/contexts/AuthContext.tsx (login, logout, token storage, current user state)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel (backend complete ✅, frontend pending npm availability)

---

## Phase 3: User Story 1 - Solo Exploration & Discovery (Priority: P1) 🎯 MVP

**Goal**: Single player spawns at home base, explores fog-of-war grid to discover tiles, manages oxygen, and surfaces to recharge

**Independent Test**: Player can spawn, move to adjacent tiles, discover content (empty/tool/hazard), track oxygen depletion, and surface after 10 discoveries to restore oxygen to 20 units

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T026 [P] [US1] Contract test for POST /api/register endpoint in backend/tests/contract/test_auth_contract.py (validate OpenAPI schema compliance, username validation, password requirements)
- [ ] T027 [P] [US1] Contract test for POST /api/login endpoint in backend/tests/contract/test_auth_contract.py (validate token format, expiry, error responses)
- [ ] T028 [P] [US1] Contract test for POST /api/discover endpoint in backend/tests/contract/test_game_actions_contract.py (validate request schema, response schema, cooldown errors, adjacency errors)
- [ ] T029 [P] [US1] Contract test for POST /api/surface endpoint in backend/tests/contract/test_game_actions_contract.py (validate 202 Accepted, duration, status transition)
- [ ] T030 [P] [US1] Contract test for GET /api/status endpoint in backend/tests/contract/test_info_contract.py (validate SubmarineStatus schema, all fields present)
- [ ] T031 [US1] Integration test for user registration flow in backend/tests/integration/test_auth_integration.py (register → verify user in DB → bcrypt hash validated)
- [ ] T032 [US1] Integration test for discovery cycle in backend/tests/integration/test_discovery_integration.py (spawn → 10 discoveries → oxygen depletion → surface → oxygen restored)
- [ ] T033 [US1] E2E test for exploration journey in tests/e2e/test_exploration.spec.ts (register → login → spawn → discover 5 tiles → verify fog-of-war updates → surface)

### Implementation for User Story 1

#### Database Models

- [ ] T034 [P] [US1] Create User model in backend/src/models/user.py (username PK, password_hash, created_at, last_login_at per data-model.md)
- [ ] T035 [P] [US1] Create Match model in backend/src/models/match.py (match_id PK, start_time, end_time, status, winner_username FK, map_configuration JSONB per data-model.md)
- [ ] T036 [P] [US1] Create Submarine model in backend/src/models/submarine.py (sub_id PK, match_id FK, username FK, position_x/y, home_base_x/y, oxygen 0-20, status enum, inventory JSONB, known_fields JSONB, travel_log JSONB, cooldowns JSONB per data-model.md)
- [ ] T037 [P] [US1] Create Event model in backend/src/models/event.py (event_id PK, match_id FK, sub_id FK, position_x/y, event_type, event_details JSONB, occurred_at per data-model.md)
- [ ] T038 [US1] Create Alembic migration for User, Match, Submarine, Event tables in backend/alembic/versions/002_user_story_1_entities.py (includes indexes: match_id+status, match_id+position, last_action_timestamp)

#### Services & Business Logic

- [ ] T039 [US1] Implement MatchService in backend/src/services/match_service.py (create_match with 32x32 map generation, 20 home_bases, 1 treasure, 60% empty / 10% tool / 10% hazard distribution per FR-008 to FR-012)
- [ ] T040 [US1] Implement SubmarineService in backend/src/services/submarine_service.py (spawn_submarine at home_base with oxygen=20, assign frequency_secret UUID per FR-014)
- [ ] T041 [US1] Implement DiscoveryService in backend/src/services/discovery_service.py (validate_adjacency 4-neighbor, apply_10s_delay, reveal_tile_content, decrement_oxygen, update_known_fields, log_to_travel_log per FR-015 to FR-020)
- [ ] T042 [US1] Implement SurfaceService in backend/src/services/surface_service.py (set_status_surfaced, schedule_60s_duration, restore_oxygen_to_20, reset_discovery_count per FR-023 to FR-025)
- [ ] T043 [US1] Implement OxygenManager in backend/src/services/oxygen_manager.py (track_oxygen_per_action, enforce_discovery_limit_10, trigger_disable_on_zero per FR-016, FR-023, FR-046)

#### API Endpoints

- [ ] T044 [US1] Implement POST /api/register endpoint in backend/src/api/auth.py (validate username regex ^[a-zA-Z0-9_]{3,20}$, password min 8 chars, hash password, create User, return 201 Created per FR-001 to FR-002)
- [ ] T045 [US1] Implement POST /api/login endpoint in backend/src/api/auth.py (validate credentials, verify password hash, create JWT token 24h expiry, update last_login_at, return 200 OK with token per FR-003)
- [ ] T046 [US1] Implement POST /api/discover endpoint in backend/src/api/game_actions.py (require JWT auth, validate adjacency, enforce cooldown 8s, call DiscoveryService, emit OpenTelemetry span, return 200 OK with tile_content per FR-015)
- [ ] T047 [US1] Implement POST /api/surface endpoint in backend/src/api/game_actions.py (require JWT auth, call SurfaceService, emit OpenTelemetry span, return 202 Accepted with duration_seconds per FR-024)
- [ ] T048 [US1] Implement GET /api/status endpoint in backend/src/api/info.py (require JWT auth, fetch submarine state from cache or DB, return SubmarineStatus schema per FR-054)

#### Cache Layer

- [ ] T049 [US1] Implement submarine cache operations in backend/src/cache/submarine_cache.py (get_submarine, update_submarine, invalidate_submarine with write-through to DB per FR-068)
- [ ] T050 [US1] Implement match state cache operations in backend/src/cache/match_cache.py (get_active_match, cache_map_configuration, get_leaderboard sorted set)

#### Frontend Components

- [ ] T051 [US1] Create Register page in frontend/src/pages/Register.tsx (form with username/password fields, validation, call POST /api/register, redirect to login on success)
- [ ] T052 [US1] Create Login page in frontend/src/pages/Login.tsx (form with username/password fields, call POST /api/login, store token in AuthContext, redirect to game)
- [ ] T053 [US1] Create Game page layout in frontend/src/pages/Game.tsx (container for MapGrid, StatusPanel, layout structure)
- [ ] T054 [US1] Create MapGrid component in frontend/src/components/MapGrid.tsx (render 32x32 grid, show only known_fields tiles, fog-of-war for undiscovered, click tile to discover)
- [ ] T055 [US1] Create StatusPanel component in frontend/src/components/StatusPanel.tsx (display position, oxygen bar 0-20, status badge, inventory list, treasure_held indicator)
- [ ] T056 [US1] Implement useGameState hook in frontend/src/hooks/useGameState.ts (poll GET /api/status every 5s, manage submarine state, trigger UI updates)
- [ ] T057 [US1] Implement authentication service in frontend/src/services/auth-service.ts (register, login, logout functions calling API endpoints)
- [ ] T058 [US1] Implement game actions service in frontend/src/services/game-service.ts (discover, surface functions calling API endpoints)

#### Observability & Logging

- [ ] T059 [US1] Add OpenTelemetry spans for discovery action in backend/src/services/discovery_service.py (span name: "discover_tile", attributes: x, y, oxygen_before, oxygen_after, tile_content)
- [ ] T060 [US1] Add custom metrics for User Story 1 in backend/src/observability/metrics.py (counter: discovery_count, histogram: discovery_latency_ms, gauge: active_oxygen_levels)
- [ ] T061 [US1] Add structured logs for critical events in backend/src/services/* (player_spawned, tile_discovered, player_surfaced with trace_id per FR-048, FR-051)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Player can register, login, spawn, discover 10 tiles, surface, and resume exploration.

---

## Phase 4: User Story 2 - Treasure Hunt & Return Victory (Priority: P2)

**Goal**: Player discovers unique treasure tile, auto-picks up treasure, receives global broadcast, navigates to home base, surfaces, and wins

**Independent Test**: Player discovers treasure at known coordinates, treasure_held becomes true, global broadcast sent, player navigates to home_base while holding treasure, surfaces at home_base, match ends with victory status

### Tests for User Story 2

- [ ] T062 [P] [US2] Contract test for GET /api/game_state endpoint in backend/tests/contract/test_info_contract.py (validate GameState schema, treasure_holder, leaderboard structure)
- [ ] T063 [US2] Integration test for treasure discovery flow in backend/tests/integration/test_treasure_integration.py (discover treasure tile → treasure_held=true → broadcast sent → verify all players receive broadcast)
- [ ] T064 [US2] Integration test for victory condition in backend/tests/integration/test_victory_integration.py (treasure_held + at home_base + surface → match status=ended, winner_username set)
- [ ] T065 [US2] E2E test for treasure hunt journey in tests/e2e/test_treasure_hunt.spec.ts (login → spawn → discover treasure → verify broadcast → navigate home → surface → verify victory)

### Implementation for User Story 2

#### Database Models

- [ ] T066 [P] [US2] Create Message model in backend/src/models/message.py (message_id PK, match_id FK, from_sub_id FK, to_sub_id_or_channel, text, sent_at per data-model.md)
- [ ] T067 [US2] Create Alembic migration for Message table in backend/alembic/versions/003_user_story_2_entities.py (includes index: match_id+to_sub_id_or_channel+sent_at DESC)

#### Services & Business Logic

- [ ] T068 [US2] Implement TreasureService in backend/src/services/treasure_service.py (auto_pickup_treasure, set_treasure_held_true, change_tile_to_empty, broadcast_treasure_discovery with "Treasure discovered at (x,y) by sub-id" per FR-021)
- [ ] T069 [US2] Implement VictoryService in backend/src/services/victory_service.py (check_victory_condition: treasure_held + at_home_base + surfaced, set_match_ended, set_winner_username, log_match_won_event per FR-028, FR-029)
- [ ] T070 [US2] Implement BroadcastService in backend/src/services/broadcast_service.py (send_global_broadcast to all players, publish to Redis pub/sub channel, create Message records per FR-038)
- [ ] T071 [US2] Update DiscoveryService in backend/src/services/discovery_service.py (detect treasure tile, call TreasureService.auto_pickup_treasure, trigger broadcast per FR-021)
- [ ] T072 [US2] Update SurfaceService in backend/src/services/surface_service.py (check if at home_base + treasure_held, call VictoryService.check_victory_condition per FR-028)

#### API Endpoints

- [ ] T073 [US2] Implement POST /api/broadcast endpoint in backend/src/api/communication.py (require JWT auth, validate message text max 500 chars, call BroadcastService, return 200 OK with message_id per FR-038)
- [ ] T074 [US2] Implement GET /api/game_state endpoint in backend/src/api/info.py (require JWT auth, fetch match status, active_players count, treasure_holder if surfaced, leaderboard sorted by distance to home, return GameState schema per FR-055, FR-056)
- [ ] T075 [US2] Implement GET /api/messages endpoint in backend/src/api/info.py (require JWT auth, fetch messages where to="ALL" or to=current_sub_id, paginate with limit/before params, return MessagesResponse schema per FR-057)

#### Cache Layer

- [ ] T076 [US2] Implement message cache operations in backend/src/cache/message_cache.py (cache_latest_messages for inbox, invalidate_on_new_message)
- [ ] T077 [US2] Update match_cache.py in backend/src/cache/match_cache.py (add update_treasure_holder, update_leaderboard sorted set by distance to home)

#### Frontend Components

- [ ] T078 [US2] Create Leaderboard component in frontend/src/components/Leaderboard.tsx (display active_players, treasure_holder with position if surfaced, top 5 players by distance to home)
- [ ] T079 [US2] Create CommsPanel component in frontend/src/components/CommsPanel.tsx (inbox showing broadcasts, send broadcast form, real-time updates via WebSocket or polling)
- [ ] T080 [US2] Update MapGrid component in frontend/src/components/MapGrid.tsx (highlight treasure tile with "★" icon if discovered, show treasure_held indicator on player's position)
- [ ] T081 [US2] Update StatusPanel component in frontend/src/components/StatusPanel.tsx (add treasure_held badge, show distance to home_base, highlight home_base on map)
- [ ] T082 [US2] Update Game page in frontend/src/pages/Game.tsx (add Leaderboard, CommsPanel, VictoryModal for match end)
- [ ] T083 [US2] Create VictoryModal component in frontend/src/components/VictoryModal.tsx (display winner username, match duration, final leaderboard, "Play Again" button)
- [ ] T084 [US2] Implement useWebSocket hook in frontend/src/hooks/useWebSocket.ts (connect to ws://localhost:8000/ws, listen for treasure_discovered, match_won events, update state)

#### WebSocket & Real-Time Updates

- [ ] T085 [US2] Implement WebSocket endpoint in backend/src/api/websocket.py (accept JWT auth via query param, maintain connection pool, broadcast events: treasure_discovered, match_won per FR-060)
- [ ] T086 [US2] Update BroadcastService in backend/src/services/broadcast_service.py (publish treasure_discovered event to WebSocket channel in addition to Messages table)

#### Observability & Logging

- [ ] T087 [US2] Add OpenTelemetry spans for treasure discovery in backend/src/services/treasure_service.py (span name: "treasure_pickup", attributes: sub_id, x, y, broadcast_sent_count)
- [ ] T088 [US2] Add OpenTelemetry spans for victory check in backend/src/services/victory_service.py (span name: "victory_check", attributes: sub_id, at_home_base, treasure_held, match_ended)
- [ ] T089 [US2] Add custom metrics for User Story 2 in backend/src/observability/metrics.py (counter: treasure_discoveries, counter: matches_won, histogram: treasure_to_home_duration_ms)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Player can explore, find treasure, and win by returning home.

---

## Phase 5: User Story 3 - Frequency Exchange & Communication (Priority: P3)

**Goal**: Two players on same tile exchange secret frequencies, enabling subsequent direct messaging and tactical coordination

**Independent Test**: Two players move to same tile, exchange frequencies, send bidirectional direct messages successfully, verify message delivery to correct recipients

### Tests for User Story 3

- [ ] T090 [P] [US3] Contract test for POST /api/exchange_frequency endpoint in backend/tests/contract/test_communication_contract.py (validate request schema, response schema, error cases: not adjacent, already exchanged)
- [ ] T091 [P] [US3] Contract test for POST /api/direct endpoint in backend/tests/contract/test_communication_contract.py (validate DirectMessageRequest schema, frequency validation, error cases: unknown frequency)
- [ ] T092 [US3] Integration test for frequency exchange flow in backend/tests/integration/test_frequency_integration.py (two players on same tile → exchange → both known_frequencies updated → verify mutual)
- [ ] T093 [US3] Integration test for direct messaging in backend/tests/integration/test_messaging_integration.py (player A has B's frequency → send direct message → B receives in inbox → A does not see in broadcast feed)
- [ ] T094 [US3] E2E test for tactical communication in tests/e2e/test_communication.spec.ts (two players register → spawn → navigate to same tile → exchange frequencies → send direct messages → verify inbox updates)

### Implementation for User Story 3

#### Services & Business Logic

- [ ] T095 [US3] Implement FrequencyService in backend/src/services/frequency_service.py (validate_same_tile, validate_not_disabled, exchange_frequencies mutually, update_known_frequencies arrays per FR-035, FR-036)
- [ ] T096 [US3] Implement DirectMessageService in backend/src/services/direct_message_service.py (validate_frequency_known, resolve_recipient_by_frequency, create_message with to=sub_id, send_to_recipient per FR-037, FR-038)
- [ ] T097 [US3] Update SubmarineService in backend/src/services/submarine_service.py (add get_submarines_at_position for collision detection, detect_encounters for encounter events)

#### API Endpoints

- [ ] T098 [US3] Implement POST /api/exchange_frequency endpoint in backend/src/api/communication.py (require JWT auth, parse target_sub_id, validate both on same tile, call FrequencyService.exchange_frequencies, return 200 OK with your_frequency + their_frequency per FR-039, FR-040)
- [ ] T099 [US3] Implement POST /api/direct endpoint in backend/src/api/communication.py (require JWT auth, validate frequency in known_frequencies, call DirectMessageService, return 200 OK with message_id per FR-039, FR-040)

#### Cache Layer

- [ ] T100 [US3] Update submarine_cache.py in backend/src/cache/submarine_cache.py (add get_submarines_at_tile for encounter detection, cache known_frequencies updates)

#### Frontend Components

- [ ] T101 [US3] Update CommsPanel component in frontend/src/components/CommsPanel.tsx (add "Direct" tab, list known_frequencies with usernames, direct message form with frequency selector)
- [ ] T102 [US3] Update MapGrid component in frontend/src/components/MapGrid.tsx (show other players on same tile with "exchange frequency" button, call POST /api/exchange_frequency on click)
- [ ] T103 [US3] Create FrequencyList component in frontend/src/components/FrequencyList.tsx (display known_frequencies with sub_id labels, click to open direct message composer)
- [ ] T104 [US3] Implement communication service in frontend/src/services/comms-service.ts (exchangeFrequency, sendDirect, sendBroadcast, getMessages functions)

#### Observability & Logging

- [ ] T105 [US3] Add OpenTelemetry spans for frequency exchange in backend/src/services/frequency_service.py (span name: "exchange_frequency", attributes: sub_id_a, sub_id_b, position_x, position_y)
- [ ] T106 [US3] Add custom metrics for User Story 3 in backend/src/observability/metrics.py (counter: frequency_exchanges, counter: direct_messages_sent, histogram: message_delivery_latency_ms)

**Checkpoint**: All user stories 1-3 should now be independently functional. Players can explore, find treasure, and communicate tactically.

---

## Phase 6: User Story 4 - EMP Combat & Treasure Drop Mechanic (Priority: P4)

**Goal**: Player uses EMP tool to disable target for 30s; if target carrying treasure receives 4+ EMP hits, treasure drops at current location

**Independent Test**: Player with EMP tool encounters treasure carrier, uses EMP 4 times within disable windows, forces treasure drop, treasure becomes discoverable at drop tile

### Tests for User Story 4

- [ ] T107 [P] [US4] Contract test for POST /api/use_tool endpoint in backend/tests/contract/test_game_actions_contract.py (validate UseToolRequest schema, tool types enum, target validation, error cases: tool not owned, target not in range)
- [ ] T108 [US4] Integration test for EMP disable flow in backend/tests/integration/test_emp_integration.py (use EMP on adjacent target → target status=disabled for 30s → disabled_count increments → target cannot move/discover)
- [ ] T109 [US4] Integration test for treasure drop mechanic in backend/tests/integration/test_treasure_drop_integration.py (treasure carrier + disabled_count=3 → 4th EMP hit → treasure_held=false → tile content=Treasure → drop event logged)
- [ ] T110 [US4] E2E test for EMP combat scenario in tests/e2e/test_emp_combat.spec.ts (player A finds treasure → player B finds EMP tool → B navigates to A → B uses EMP 4 times → verify A drops treasure → B discovers dropped treasure)

### Implementation for User Story 4

#### Services & Business Logic

- [ ] T111 [US4] Implement ToolService in backend/src/services/tool_service.py (use_emp: validate target adjacent, set_status_disabled for 30s, increment_disabled_count, check_treasure_drop_threshold, schedule_re_enable after 30s per FR-030 to FR-034)
- [ ] T112 [US4] Implement ToolService.use_sonar in backend/src/services/tool_service.py (reveal 7x7 area around position, update known_fields with revealed tiles, apply random glitch 10% chance per FR-041)
- [ ] T113 [US4] Implement ToolService.use_repair_kit in backend/src/services/tool_service.py (restore oxygen by 5 units, cap at 20, clear disabled_count if used by self)
- [ ] T114 [US4] Update TreasureService in backend/src/services/treasure_service.py (add drop_treasure: set_treasure_held_false, update_tile_content_to_treasure, log_treasure_drop_event per FR-033)
- [ ] T115 [US4] Update DiscoveryService in backend/src/services/discovery_service.py (detect tool tiles: EMP, sonar, repair_kit; add to inventory, remove from tile per FR-019)

#### API Endpoints

- [ ] T116 [US4] Implement POST /api/use_tool endpoint in backend/src/api/game_actions.py (require JWT auth, validate tool in inventory, route to ToolService based on tool type, remove tool from inventory, emit OpenTelemetry span, return UseToolResponse per FR-024 to FR-030)

#### Cache Layer

- [ ] T117 [US4] Update submarine_cache.py in backend/src/cache/submarine_cache.py (add update_disabled_status with 30s TTL, update_disabled_count, update_inventory on tool usage)

#### Frontend Components

- [ ] T118 [US4] Update StatusPanel component in frontend/src/components/StatusPanel.tsx (display inventory items as clickable buttons: "Use EMP", "Use Sonar", "Use Repair Kit")
- [ ] T119 [US4] Create ToolUsageModal component in frontend/src/components/ToolUsageModal.tsx (for EMP: show list of adjacent players as targets, for sonar: show 7x7 reveal animation, for repair kit: show oxygen restore confirmation)
- [ ] T120 [US4] Update MapGrid component in frontend/src/components/MapGrid.tsx (show disabled players with "⚡" badge, show dropped treasure at tile if known_fields contains treasure after drop)
- [ ] T121 [US4] Update game service in frontend/src/services/game-service.ts (useTool function calling POST /api/use_tool with tool type and optional target_sub_id)

#### Background Jobs & Scheduling

- [ ] T122 [US4] Implement disable scheduler in backend/src/services/disable_scheduler.py (track disabled submarines with expiry timestamps, re-enable after 30s, update cache and DB)

#### Observability & Logging

- [ ] T123 [US4] Add OpenTelemetry spans for EMP usage in backend/src/services/tool_service.py (span name: "use_emp", attributes: attacker_sub_id, target_sub_id, disabled_count_after, treasure_dropped)
- [ ] T124 [US4] Add custom metrics for User Story 4 in backend/src/observability/metrics.py (counter: emp_hits, counter: treasure_drops, counter: tools_used by type)

**Checkpoint**: All user stories 1-4 should now be independently functional. Players can explore, find treasure, communicate, and engage in EMP combat.

---

## Phase 7: User Story 5 - Multi-Player Web UI with Fog-of-War & Replay (Priority: P5)

**Goal**: Each player accesses web interface showing personal fog-of-war map, discovered tiles, inventory, status, messages, and timeline replay of path and encounters

**Independent Test**: Player logs into web UI, sees known_fields rendered as grid, clicks to use tool (calls API), sends/receives messages, scrubs through travel_log timeline

### Tests for User Story 5

- [ ] T125 [P] [US5] Contract test for GET /api/replay endpoint in backend/tests/contract/test_info_contract.py (validate ReplayResponse schema, event filtering by sub_id, time range filtering)
- [ ] T126 [US5] E2E test for UI rendering in tests/e2e/test_ui_rendering.spec.ts (login → verify map grid loads → verify fog-of-war hides undiscovered tiles → discover tile → verify tile revealed in UI)
- [ ] T127 [US5] E2E test for replay timeline in tests/e2e/test_replay.spec.ts (player completes 20 actions → open replay panel → scrub through timeline → verify positions and events displayed correctly)
- [ ] T128 [US5] Frontend unit test for MapGrid rendering in frontend/tests/unit/MapGrid.test.tsx (render with mock known_fields → verify tile count → verify fog-of-war cells have correct class)

### Implementation for User Story 5

#### API Endpoints

- [ ] T129 [US5] Implement GET /api/replay endpoint in backend/src/api/info.py (require JWT auth, parse from/to/sub_id query params, fetch Events from DB, filter by criteria, return ReplayResponse schema per FR-058)

#### Frontend Components

- [ ] T130 [US5] Create ReplayTimeline component in frontend/src/components/ReplayTimeline.tsx (fetch GET /api/replay, display events as timeline, scrubber to step through events, highlight position on map for each event)
- [ ] T131 [US5] Update MapGrid component in frontend/src/components/MapGrid.tsx (add tile click handlers: discover adjacent tile → call POST /api/discover → show loading spinner for 10s → update on response)
- [ ] T132 [US5] Create App.tsx main app component in frontend/src/App.tsx (React Router with routes: /register, /login, /game, /replay, protected routes requiring authentication)
- [ ] T133 [US5] Implement responsive grid layout in frontend/src/components/MapGrid.tsx (32x32 grid scales to viewport, zoom controls, pan on drag, mobile-friendly touch gestures)
- [ ] T134 [US5] Add visual polish to UI in frontend/src/styles/ (CSS for fog-of-war gradient, tile icons: empty=ocean wave, tool=wrench, hazard=warning, treasure=star, home_base=house, submarine=ship)

#### Frontend State Management

- [ ] T135 [US5] Update useGameState hook in frontend/src/hooks/useGameState.ts (manage known_fields map, update on discovery, manage submarine position, oxygen bar animation)
- [ ] T136 [US5] Implement useReplay hook in frontend/src/hooks/useReplay.ts (fetch replay data, manage timeline state, step forward/backward through events, sync map position with timeline scrubber)

#### Observability & Logging

- [ ] T137 [US5] Add custom metrics for User Story 5 in backend/src/observability/metrics.py (counter: replay_requests, histogram: replay_query_latency_ms, gauge: ui_polling_rate)

**Checkpoint**: All 5 user stories should now be independently functional. Full game experience available via Web UI and MCP tools.

---

## Phase 8: MCP Tool Integration (Cross-Cutting)

**Purpose**: Enable AI agents to play game via MCP tools wrapping REST API

**Dependencies**: Requires User Stories 1-4 API endpoints complete

- [ ] T138 [P] Create MCP tool schemas in mcp-server/src/tools/schemas.py (RegisterRequest, LoginRequest, DiscoverRequest, SurfaceRequest, UseToolRequest, ExchangeFrequencyRequest, BroadcastRequest, DirectMessageRequest per FR-062)
- [ ] T139 [P] Implement HTTP client wrapper in mcp-server/src/api_client.py (httpx async client, bearer token management, base URL configuration, error handling per FR-063)
- [ ] T140 [P] Implement register_user MCP tool in mcp-server/src/tools/auth_tools.py (call POST /api/register, return human-readable summary + structured result per FR-064)
- [ ] T141 [P] Implement login_user MCP tool in mcp-server/src/tools/auth_tools.py (call POST /api/login, store token in context, return summary per FR-064)
- [ ] T142 [P] Implement discover_field MCP tool in mcp-server/src/tools/game_tools.py (call POST /api/discover with auth token, return summary: "Discovered empty tile at (5,7). Oxygen: 18/20. Discoveries: 3/10." per FR-064)
- [ ] T143 [P] Implement surface MCP tool in mcp-server/src/tools/game_tools.py (call POST /api/surface, return summary with duration and completion time)
- [ ] T144 [P] Implement use_tool MCP tool in mcp-server/src/tools/game_tools.py (call POST /api/use_tool, return summary based on tool type: EMP hit result, sonar reveal, repair kit oxygen restored)
- [ ] T145 [P] Implement exchange_frequency MCP tool in mcp-server/src/tools/communication_tools.py (call POST /api/exchange_frequency, return summary: "Exchanged frequencies with sub-player_42. You can now send direct messages.")
- [ ] T146 [P] Implement broadcast_message MCP tool in mcp-server/src/tools/communication_tools.py (call POST /api/broadcast, return summary with message_id)
- [ ] T147 [P] Implement send_direct_message MCP tool in mcp-server/src/tools/communication_tools.py (call POST /api/direct, return summary with recipient sub_id)
- [ ] T148 [P] Implement get_status MCP tool in mcp-server/src/tools/info_tools.py (call GET /api/status, return summary: "Position: (5,7). Oxygen: 18/20. Status: submerged. Inventory: [EMP, sonar]. Treasure: false.")
- [ ] T149 [P] Implement get_game_state MCP tool in mcp-server/src/tools/info_tools.py (call GET /api/game_state, return summary with active players, treasure holder, leaderboard top 5)
- [ ] T150 [P] Implement get_messages MCP tool in mcp-server/src/tools/info_tools.py (call GET /api/messages, return summary with message count and latest 5 messages)
- [ ] T151 [P] Implement get_replay MCP tool in mcp-server/src/tools/info_tools.py (call GET /api/replay, return summary with event count and timeline)
- [ ] T152 Create MCP server entry point in mcp-server/src/server.py (initialize MCP SDK server, register all tools, start JSON-RPC server on port 3000 per FR-061)
- [ ] T153 [P] Integration test for MCP tools in mcp-server/tests/integration/test_mcp_tools.py (register via MCP → login via MCP → discover via MCP → verify API called correctly)

---

## Phase 9: Inactivity Timeout & Match Management (Cross-Cutting)

**Purpose**: Handle inactive players and match lifecycle

**Dependencies**: Requires Submarine and Match models complete

- [ ] T154 Implement inactivity monitor in backend/src/services/inactivity_monitor.py (background job checking last_action_timestamp every 60s, mark destroyed if >10 min, drop treasure if held, log event per FR-022)
- [ ] T155 Update SubmarineService in backend/src/services/submarine_service.py (add mark_destroyed: set status=destroyed, drop_treasure_if_held, make_slot_available)
- [ ] T156 Implement match reset logic in backend/src/services/match_service.py (trigger on all_destroyed or timeout, respawn all submarines, regenerate treasure location, reset map per FR-029 edge case)
- [ ] T157 Add background job scheduler in backend/src/main.py (startup event: launch inactivity_monitor, match_reset_monitor as asyncio tasks)

---

## Phase 10: Random Events & Hazards (Cross-Cutting)

**Purpose**: Trigger probabilistic random events on actions

**Dependencies**: Requires DiscoveryService and ToolService complete

- [ ] T158 Implement RandomEventService in backend/src/services/random_event_service.py (trigger_random_event with 10% probability, event types: leak, strong_current, sonar_glitch, ghost_signal per FR-041)
- [ ] T159 Implement leak hazard in backend/src/services/random_event_service.py (lose 1 oxygen, skip next action cycle, log event per FR-042)
- [ ] T160 Implement strong_current hazard in backend/src/services/random_event_service.py (teleport submarine ±1-2 tiles within bounds, update position, log event)
- [ ] T161 Implement sonar_glitch hazard in backend/src/services/random_event_service.py (scramble next sonar result, show incorrect tile content for 1 turn)
- [ ] T162 Implement ghost_signal hazard in backend/src/services/random_event_service.py (add fake frequency UUID to known_frequencies, direct messages to ghost fail silently)
- [ ] T163 Update DiscoveryService in backend/src/services/discovery_service.py (call RandomEventService.trigger_random_event after tile reveal, apply hazard if triggered)

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T164 [P] Add API documentation in backend/docs/api.md (link to OpenAPI spec at /docs, authentication guide, rate limits, error codes reference)
- [ ] T165 [P] Add developer quickstart validation script in scripts/validate_quickstart.sh (run through quickstart.md steps, verify all services start, run smoke tests)
- [ ] T166 [P] Add database seed script in backend/scripts/seed_test_data.py (create 3 test users: alice, bob, charlie with password testpass123, create 1 active match with 20 submarines, place treasure at known location)
- [ ] T167 [P] Add performance optimization for discovery queries in backend/src/services/discovery_service.py (add Redis cache for known_fields to avoid DB round-trip on every status check)
- [ ] T168 [P] Add security hardening in backend/src/api/auth.py (rate limit login attempts 5 per minute per IP, add CORS whitelist from config, validate JWT issuer/audience)
- [ ] T169 [P] Add frontend error boundaries in frontend/src/components/ErrorBoundary.tsx (catch React errors, display user-friendly message, log to backend)
- [ ] T170 [P] Add frontend loading states in frontend/src/components/ (skeleton loaders for map grid, status panel, messages while fetching)
- [ ] T171 Code cleanup pass: run ruff format and mypy in backend/, prettier in frontend/, fix all type errors and linting warnings
- [ ] T172 Documentation: update README.md at repository root with project overview, architecture diagram, quickstart link, constitution link
- [ ] T173 Run full E2E test suite in tests/e2e/ covering all 5 user stories, verify all pass
- [ ] T174 Run quickstart.md validation: fresh clone → follow setup steps → verify all services start → run seed script → verify 20 players can join match

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Builds on US1 models but independently testable
  - User Story 3 (P3): Can start after Foundational - Independently testable (requires two players but no treasure mechanics)
  - User Story 4 (P4): Can start after Foundational - Independently testable (EMP mechanics separate from treasure/communication)
  - User Story 5 (P5): Can start after US1-4 API endpoints complete - UI layer over existing APIs
- **MCP Integration (Phase 8)**: Depends on US1-4 API endpoints complete
- **Inactivity/Match Management (Phase 9)**: Depends on Submarine/Match models from US1
- **Random Events (Phase 10)**: Depends on DiscoveryService from US1
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) 🎯 MVP**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 with treasure mechanics but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independently testable (requires encounter detection but no treasure/combat)
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independently testable (EMP mechanics work without treasure but integrate with US2 for treasure drop)
- **User Story 5 (P5)**: Can start after US1-4 API endpoints complete - UI layer consuming existing APIs

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services (services depend on model schemas)
- Services before endpoints (endpoints call services)
- Cache layer alongside services (services use cache)
- Frontend components after API endpoints (UI consumes API)
- Observability after core logic (instrumentation added to existing code)
- Story complete before moving to next priority

### Parallel Opportunities

- **All Setup tasks (T002-T010)** marked [P] can run in parallel (different directories)
- **All Foundational tasks (T014-T025)** marked [P] can run in parallel (within Phase 2)
- **Once Foundational phase completes**, all user story phases (3-7) can start in parallel if team capacity allows
- **Within each user story**:
  - All contract tests marked [P] can run in parallel (different test files)
  - All models marked [P] can run in parallel (different model files)
  - All frontend components marked [P] can run in parallel (different component files)
- **MCP tools (T140-T151)** marked [P] can all be implemented in parallel (different tool files)
- **Polish tasks (T164-T174)** marked [P] can run in parallel (different concerns)

---

## Parallel Example: User Story 1

```bash
# Write all contract tests together (different files):
T026: backend/tests/contract/test_auth_contract.py (POST /api/register, POST /api/login)
T027: backend/tests/contract/test_game_actions_contract.py (POST /api/discover, POST /api/surface)
T028: backend/tests/contract/test_info_contract.py (GET /api/status)

# Launch all models together (different files):
T034: backend/src/models/user.py
T035: backend/src/models/match.py
T036: backend/src/models/submarine.py
T037: backend/src/models/event.py

# Launch all frontend components together (different files):
T054: frontend/src/components/MapGrid.tsx
T055: frontend/src/components/StatusPanel.tsx
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) 🎯

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T025) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T026-T061)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Register user → Login → Spawn → Discover 10 tiles → Surface → Oxygen restored to 20
   - Verify OpenTelemetry traces captured for discovery actions
   - Verify Web UI renders fog-of-war map correctly
5. Deploy/demo MVP if ready

**MVP delivers**: Single-player exploration game with oxygen management, fog-of-war discovery, and surfacing mechanics. Immediately playable and demonstrable.

### Incremental Delivery

1. **Foundation** (Phases 1-2): Setup + Foundational → Foundation ready
2. **MVP** (Phase 3): User Story 1 → Test independently → Deploy/Demo (exploration game!)
3. **Treasure Hunt** (Phase 4): User Story 2 → Test independently → Deploy/Demo (adds win condition!)
4. **Social Tactics** (Phase 5): User Story 3 → Test independently → Deploy/Demo (adds communication!)
5. **Combat Dynamics** (Phase 6): User Story 4 → Test independently → Deploy/Demo (adds EMP combat!)
6. **Full UI/UX** (Phase 7): User Story 5 → Test independently → Deploy/Demo (polished experience!)
7. **AI Agents** (Phase 8): MCP Integration → Deploy/Demo (AI agents can play!)
8. **Production Ready** (Phases 9-11): Inactivity timeout, random events, polish → Production deployment

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. **Week 1**: Team completes Setup + Foundational together (T001-T025)
2. **Week 2**: Once Foundational is done:
   - **Developer A**: User Story 1 (T026-T061) - MVP exploration
   - **Developer B**: User Story 2 (T062-T089) - Treasure hunt
   - **Developer C**: User Story 3 (T090-T106) - Communication
3. **Week 3**: 
   - **Developer A**: User Story 4 (T107-T124) - EMP combat
   - **Developer B**: User Story 5 (T125-T137) - Web UI polish
   - **Developer C**: MCP Integration (T138-T153) - AI agent tools
4. **Week 4**: Team integrates cross-cutting concerns together (T154-T174)

Stories complete and integrate independently. Each developer can test their story in isolation.

---

## Task Summary

**Total Tasks**: 174

**Tasks by Phase**:
- Phase 1 (Setup): 10 tasks
- Phase 2 (Foundational): 15 tasks
- Phase 3 (User Story 1 - MVP): 36 tasks
- Phase 4 (User Story 2): 28 tasks
- Phase 5 (User Story 3): 17 tasks
- Phase 6 (User Story 4): 18 tasks
- Phase 7 (User Story 5): 13 tasks
- Phase 8 (MCP Integration): 16 tasks
- Phase 9 (Inactivity Timeout): 4 tasks
- Phase 10 (Random Events): 6 tasks
- Phase 11 (Polish): 11 tasks

**Parallel Opportunities**: 89 tasks marked [P] can run in parallel (51% of total)

**Independent Test Criteria**:
- **US1**: Player spawns → discovers 10 tiles → surfaces → oxygen restored ✅
- **US2**: Player discovers treasure → navigates home → surfaces → wins ✅
- **US3**: Two players meet → exchange frequencies → send direct messages ✅
- **US4**: Player uses EMP 4 times → treasure drops → becomes discoverable ✅
- **US5**: Player opens UI → sees fog-of-war → scrubs replay timeline ✅

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 61 tasks
- Delivers: Single-player exploration game with oxygen management and fog-of-war
- Immediately playable and demonstrable
- Validates core architecture before adding multiplayer complexity

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests written FIRST, must FAIL before implementation (TDD)
- Verify tests fail → implement → verify tests pass → commit
- Stop at any checkpoint to validate story independently
- Constitution gates validated: Simplicity (dependencies justified), Explicitness (OpenAPI + types), E2E Coverage (test plan per story), Diagnostic Errors (error_code + context), Evolution Safety (API versioning + migrations)
- OpenTelemetry instrumentation added throughout (FR-047 to FR-052 compliance)
- All file paths are absolute based on plan.md project structure
