# Feature Specification: Ras's Deep Treasure Game

**Feature Branch**: `001-deep-treasure-game`  
**Created**: 2025-10-24  
**Status**: Draft  
**Input**: Multiplayer submarine treasure hunt game with OpenAPI endpoints (for human players via Web UI) and MCP tool wrappers (for AI agent players) supporting 20 concurrent players

## Clarifications

### Session 2025-10-24

- Q: Initial and maximum oxygen value for submarine resource management? → A: 20 units (tight: 2 surface cycles before depletion; renamed from "energy" to "oxygen" for thematic consistency)
- Q: Observability requirements for debugging 20-player concurrency, timing, and combat mechanics? → A: Full observability with OpenTelemetry (structured logs + metrics + distributed tracing)
- Q: How do MCP (Model Context Protocol) tools integrate with game server and OpenAPI endpoints? → A: MCP tools wrap OpenAPI endpoints (consistent interface; tools call /api/* endpoints; enables both human and AI agent players)
- Q: Data persistence strategy for match state, submarine data, and crash recovery? → A: Persistent database with in-memory cache (durability + performance; enables crash recovery and historical match replay)
- Q: Inactivity timeout threshold for marking submarines as destroyed/removed? → A: 10 minutes (generous; allows reconnection tolerance without indefinitely stalling matches)
- Q: Authentication mechanism for players? → A: Simple username/password authentication with registration (username + password; no email verification required)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Solo Exploration & Discovery (Priority: P1) 🎯 MVP

A single player spawns at their home base, explores the fog-of-war ocean grid to discover empty tiles, tools, and hazards, and must surface every 10 discoveries to recharge oxygen.

**Why this priority**: Core gameplay loop; establishes movement, discovery mechanics, oxygen management, and timing constraints. Delivers immediate playable value without multiplayer complexity.

**Independent Test**: Player can spawn, move to adjacent tiles, discover content (empty/tool/hazard), track oxygen, and be forced to surface after 10 discoveries. Verifiable by completing a 10-discovery exploration cycle ending in successful surface.

**Acceptance Scenarios**:

1. **Given** a player spawns at their assigned home_base `(x,y)`, **When** they request to discover an adjacent tile (4-neighbor), **Then** the tile content is revealed after 10 seconds, oxygen decreases by 1, known_fields map updates, and discovery_count increments
2. **Given** a player has made 10 discoveries, **When** they attempt an 11th discovery, **Then** the system prevents the action and requires surface command
3. **Given** a player issues surface command at any location, **When** the 60-second surface duration completes, **Then** oxygen is fully restored to 20 units, discovery_count resets to 0, and the player can resume exploration
4. **Given** a player discovers a tool tile, **When** the tile is revealed, **Then** the tool is automatically added to inventory and the tile becomes empty
5. **Given** a player discovers a hazard tile (e.g., leak), **When** the hazard triggers, **Then** oxygen decreases by 1, the player's next action is skipped (delay imposed), and the event is logged

---

### User Story 2 - Treasure Hunt & Return Victory (Priority: P2)

A player discovers the unique treasure tile, automatically picks it up, receives a global broadcast announcing their find, and must navigate back to their home base to surface and win.

**Why this priority**: Introduces the win condition and strategic navigation objective. Builds on exploration mechanics with asymmetric information (all players know who has treasure and where it was found).

**Independent Test**: Player discovers treasure tile, receives auto-pickup confirmation, sees global broadcast, navigates to home_base while carrying treasure, surfaces at home_base, and achieves victory status. Verifiable by completing treasure→home→surface sequence.

**Acceptance Scenarios**:

1. **Given** a player discovers the treasure tile, **When** the discovery completes, **Then** treasure_held becomes true, a global broadcast "Treasure discovered at (x,y) by sub-id" is sent to all players, and the tile content changes to empty
2. **Given** a player is carrying treasure and reaches their home_base, **When** they issue surface command at home_base, **Then** the game declares victory for that player and the match ends (or resets depending on configuration)
3. **Given** a player carrying treasure, **When** they move across the map, **Then** their position updates normally (no speed or oxygen penalty for carrying treasure)

---

### User Story 3 - Frequency Exchange & Communication (Priority: P3)

Two players occupying the same tile can exchange secret frequencies, enabling subsequent direct messaging and tactical coordination or negotiation.

**Why this priority**: Adds social/tactical layer without blocking core gameplay. Enables alliances, deception, and strategic communication once players encounter each other.

**Independent Test**: Two players move to the same tile, exchange frequencies, send direct messages to each other, and broadcast to known frequencies. Verifiable by successful frequency exchange followed by bidirectional direct messaging.

**Acceptance Scenarios**:

1. **Given** two players A and B are on the same tile and both are not disabled, **When** player A requests frequency exchange with B, **Then** both players add each other's frequency to known_frequencies and receive confirmation
2. **Given** player A has player B's frequency in known_frequencies, **When** A sends a direct message to B's frequency, **Then** B receives the message in their inbox with timestamp and sender info
3. **Given** player A has N known frequencies, **When** A broadcasts a message, **Then** all N players with those frequencies receive the broadcast in their inbox
4. **Given** player A is disabled, **When** A attempts to send a direct message, **Then** the system prevents the action (broadcasts still allowed)

---

### User Story 4 - EMP Combat & Treasure Drop Mechanic (Priority: P4)

A player uses an EMP tool to disable a target on the same tile for 30 seconds; if the target is carrying treasure and receives 4+ EMP hits while disabled, they drop the treasure at their current location.

**Why this priority**: Introduces tactical combat and treasure defense/theft dynamics. Requires Stories 1-3 for context (exploration, treasure, encounters).

**Independent Test**: Player with EMP tool encounters treasure carrier, uses EMP 4 times within disable windows, forces treasure drop, and the treasure becomes discoverable at the drop tile. Verifiable by cycling through disable→increment→drop sequence.

**Acceptance Scenarios**:

1. **Given** player A has an EMP tool and is on the same tile as player B, **When** A uses EMP targeting B, **Then** B's status becomes "disabled" for 30 seconds, B's disabled_count increments by 1, and B cannot move/discover/use tools/send direct messages
2. **Given** player B is disabled and carrying treasure with disabled_count = 3, **When** B receives a 4th EMP hit (disabled_count reaches 4), **Then** treasure_held becomes false, the treasure drops at B's current tile (tile content becomes Treasure), and a drop event is logged
3. **Given** a disabled player, **When** 30 seconds elapse, **Then** status returns to "submerged" and the player can resume normal actions (disabled_count persists until surface)
4. **Given** a player surfaces, **When** the surface completes, **Then** disabled_count resets to 0

---

### User Story 5 - Multi-Player Web UI with Fog-of-War & Replay (Priority: P5)

Each player accesses a web interface showing their personal fog-of-war map, discovered tiles, inventory, status, messages, and a timeline replay of their path and encounters.

**Why this priority**: Essential for usability but can be developed after backend mechanics are stable. Delivers visual feedback and enhances player experience.

**Independent Test**: Player logs into web UI, sees their known_fields rendered as a grid, clicks to use a tool (calls API), sends/receives messages, and scrubs through their travel_log timeline. Verifiable by UI interaction completing expected API calls and UI updates.

**Acceptance Scenarios**:

1. **Given** a player is logged into the web UI, **When** the UI polls `/api/status`, **Then** the map grid renders only known_fields with appropriate icons (empty/tool/hazard/sub/treasure), current position highlighted
2. **Given** a player views their status panel, **When** energy, inventory, or status changes (via polling or WebSocket), **Then** the UI updates in real-time without full page reload
3. **Given** a player has travel_log entries, **When** they open the timeline/replay panel, **Then** they can scrub through past positions and events (step-by-step playback)
4. **Given** a player clicks "Use Tool: Sonar" in the UI, **When** the click is processed, **Then** the UI calls `POST /api/use_tool { tool: "sonar" }` and displays the result (adjacent tile hints or scrambled info if glitched)
5. **Given** the game state includes a treasure holder, **When** the leaderboard panel loads, **Then** it displays the treasure holder's sub-id and their distance to home_base (calculated or estimated)

---

### Edge Cases

- **Multiple Players on Same Tile**: System allows multiple subs on one tile; encounter event triggers for each pair. EMP usage resolves by first-come timestamp (tie-break by lowest sub_id).
- **Simultaneous Discovery Attempts**: If two players attempt to discover the treasure tile simultaneously, the server processes by timestamp; winner gets treasure, loser gets empty tile result.
- **EMP During Surface**: Disabled players cannot be further disabled (status overrides); EMP hits during surface are ignored or queued until submerged (server decision).
- **Boundary/Out-of-Bounds Movement**: Discover requests for tiles outside `[0,MAX_X] x [0,MAX_Y]` return error; strong current teleports are bounded to valid coordinates.
- **Ghost Signal Injection**: Random event adds a fake frequency to a player's known_frequencies; direct messages to ghost frequencies are silently dropped or return error.
- **Tool Depletion**: Each tool (EMP, sonar, repair_kit, booster) is single-use; using a tool removes it from inventory. Discovering another tool tile adds a new instance.
- **Oxygen Depletion**: If oxygen reaches 0, player cannot discover new tiles (must surface immediately); player becomes vulnerable and disabled until surfaced.
- **Inactive/Dropped Players**: If a player disconnects or becomes inactive for 10 minutes (no API calls with valid session token), their submarine status becomes "destroyed", any carried treasure drops at current tile, and the player slot becomes available for new players to join the match.
- **Match Reset**: If all subs are destroyed or treasure remains unclaimed past a timeout, server can reset the match (respawn all subs, regenerate treasure location).
- **Cache Invalidation**: If in-memory cache becomes inconsistent with database (e.g., partial write failure), system reloads affected submarine state from database and logs discrepancy event with OpenTelemetry trace for investigation.

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & User Management**

- **FR-001**: System MUST provide user registration via POST /api/register accepting username (unique, 3-20 characters, alphanumeric + underscore) and password (minimum 8 characters)
- **FR-002**: System MUST hash passwords using a secure algorithm (e.g., bcrypt, argon2) before storing; plaintext passwords MUST NOT be persisted
- **FR-003**: System MUST provide user login via POST /api/login accepting username and password; on success, return a session token (JWT or opaque token) valid for 24 hours
- **FR-004**: System MUST validate session tokens on all authenticated API endpoints; expired or invalid tokens return 401 Unauthorized with clear error message
- **FR-005**: System MUST associate each submarine with the authenticated user's username; submarine_id format: "sub-{username}"
- **FR-006**: System MUST prevent duplicate active submarines per user; if user joins while already in match, return error with current submarine status

**Game Initialization & Configuration**

- **FR-007**: System MUST support exactly 20 concurrent player submarines (one per authenticated user session)
- **FR-008**: System MUST generate a 2D grid map with configurable dimensions (default 32x32 for 20 players; minimum 30x30)
- **FR-009**: System MUST place exactly 1 treasure tile randomly on the map at match start
- **FR-010**: System MUST assign 20 unique home_base coordinates evenly spaced around the map perimeter (clockwise indexing P1..P20)
- **FR-011**: System MUST assign each submarine a unique secret frequency at spawn
- **FR-012**: System MUST populate the map with approximately 60% empty tiles, 10% tool tiles, 10% hazard tiles (remaining tiles are home bases and treasure)

**Submarine State & Movement**

- **FR-013**: Each submarine MUST track: id (sub-{username}), username, position (x,y), home_base (x,y), oxygen (integer 0-20), status (submerged|surfaced|disabled|destroyed), last_action_timestamp, inventory (array of tools), treasure_held (boolean), disabled_count (integer), frequency_secret, known_frequencies (array), known_fields (map of discovered tiles), travel_log (array of position+event+timestamp), cooldowns (map of action→remaining_ms), messages (array of received messages)
- **FR-014**: Submarines MUST spawn at their assigned home_base coordinates with status "submerged" and oxygen at maximum (20 units)
- **FR-015**: Discovery action MUST target a tile adjacent to current position (4-neighbor: north/south/east/west) and enforce a 10-second server-side delay before completion
- **FR-016**: Discovery action MUST decrement oxygen by 1 unit per discovery

**Discovery & Fog-of-War**

- **FR-017**: Each player MUST have a personal known_fields map; only discovered tiles are visible to that player
- **FR-018**: Discovering an empty tile MUST reveal it as empty in known_fields with no side effects
- **FR-019**: Discovering a tool tile MUST automatically add the tool to inventory, update known_fields to show empty, and log the event
- **FR-020**: Discovering a hazard tile MUST trigger the hazard effect (e.g., leak: lose 1 oxygen + skip next action cycle; strong current: teleport ±1-2 tiles within bounds) and update known_fields
- **FR-021**: Discovering the treasure tile MUST auto-pickup the treasure (set treasure_held=true), send a global broadcast "Treasure discovered at (x,y) by sub-id" to all players, and change the tile content to empty
- **FR-022**: System MUST track last_action_timestamp for each submarine; if no action received for 10 minutes, submarine status becomes "destroyed", any held treasure drops at current tile, and player slot becomes available

**Surfacing & Oxygen Management**

- **FR-023**: System MUST enforce mandatory surfacing after every 10 discoveries (discovery_count threshold)
- **FR-024**: Surfacing MUST last exactly 60 seconds, during which the submarine cannot move, discover, or use tools (broadcasts allowed)
- **FR-025**: Surfacing MUST fully restore oxygen to 20 units and reset discovery_count to 0
- **FR-026**: Surfacing MUST reset disabled_count to 0

**Treasure & Victory**

- **FR-027**: A submarine carrying treasure (treasure_held=true) MUST be able to move normally (no speed or oxygen penalty)
- **FR-028**: Surfacing at home_base while carrying treasure MUST trigger a victory condition for that player
- **FR-029**: Victory MUST end the match or trigger a match reset (server configuration determines behavior)

**EMP Combat & Disable Mechanics**

- **FR-030**: EMP tool usage MUST target a specific submarine on the same tile
- **FR-031**: EMP hit MUST set target status to "disabled" for exactly 30 seconds (non-stacking duration) and increment target's disabled_count by 1
- **FR-032**: Disabled submarines MUST NOT be able to move, discover, use tools, or send direct messages (broadcasts allowed)
- **FR-033**: If disabled_count >= 4 while carrying treasure, the submarine MUST drop the treasure at its current tile (treasure_held becomes false, tile content becomes Treasure)
- **FR-034**: Multiple EMP hits within 30 seconds MUST NOT extend the disable duration but MUST increment disabled_count each time

**Frequency Exchange & Communication**

- **FR-035**: Frequency exchange MUST only succeed when both submarines are on the same tile and neither is disabled
- **FR-036**: Successful frequency exchange MUST add each submarine's frequency to the other's known_frequencies list
- **FR-037**: Direct messaging MUST require the recipient's frequency in the sender's known_frequencies
- **FR-038**: Direct messages MUST include: sender id, message text, timestamp, and be appended to recipient's messages array
- **FR-039**: Broadcast messages MUST be sent to all frequencies in the sender's known_frequencies (or "ALL" channel if server enables global broadcast)
- **FR-040**: Disabled submarines MUST NOT be able to send direct messages but CAN send broadcasts

**Random Events**

- **FR-041**: System MUST trigger random events probabilistically on discovery or tool usage: leak (lose 1 oxygen + skip next action), strong current (teleport ±1-2 tiles bounded), sonar glitch (scrambled info for 1 turn), ghost signal (fake frequency added)
- **FR-042**: Random events MUST be logged in the submarine's travel_log with event type and parameters

**Concurrency & Timing**

- **FR-043**: System MUST process actions by timestamp (first-come); ties resolved by lowest sub_id
- **FR-044**: System MUST enforce a rate limit: maximum 1 active discover action per player at any time
- **FR-045**: Encounters (multiple subs on same tile) MUST trigger for each pair present and enable frequency exchange + EMP usage
- **FR-046**: When oxygen reaches 0, submarine status MUST become "disabled" (cannot discover or move) until surfaced; submarine becomes vulnerable to EMP and other player actions

**Observability & Instrumentation**

- **FR-047**: System MUST implement OpenTelemetry instrumentation for distributed tracing across all API endpoints and internal operations
- **FR-048**: System MUST emit structured logs (JSON format) including: timestamp, trace_id, span_id, submarine_id, action_type, outcome (success/failure), latency_ms, and contextual metadata (position, oxygen_level, status)
- **FR-049**: System MUST collect metrics for: action counts (by type), action latencies (p50/p95/p99), concurrent player count, active discoveries in-flight, EMP hit rate, treasure discovery events, error rates (by type), oxygen depletion events, inactivity timeouts
- **FR-050**: System MUST trace critical paths: discover action (request → validation → delay → completion), EMP usage (target resolution → disable application → event broadcast), treasure pickup (discovery → broadcast → state update), frequency exchange (collision detection → mutual update)
- **FR-051**: System MUST emit custom events for game-specific telemetry: user_registered, user_logged_in, player_spawned, tile_discovered, treasure_found, emp_hit, frequency_exchanged, player_surfaced, player_inactive_timeout, match_won, match_reset
- **FR-052**: All errors MUST include: error_code, operation_name, submarine_id, request_context (action attempted, inputs), expected_vs_actual state mismatch details, and OpenTelemetry trace context for correlation

**Web UI & API**

- **FR-053**: System MUST provide RESTful API endpoints: POST /api/register, POST /api/login, POST /api/discover, POST /api/surface, POST /api/use_tool, POST /api/exchange_frequency, POST /api/broadcast, POST /api/direct, GET /api/status, GET /api/game_state, GET /api/messages, GET /api/replay
- **FR-054**: Web UI MUST provide registration form (username + password fields) and login form (username + password fields)
- **FR-055**: Web UI MUST render player's known_fields as a 2D grid with fog-of-war (undiscovered tiles hidden)
- **FR-056**: Web UI MUST display submarine status panel (position, oxygen level, status, inventory, treasure_held)
- **FR-057**: Web UI MUST display communications panel (inbox for broadcasts + direct messages; send interface)
- **FR-058**: Web UI MUST display leaderboard showing treasure holder (if any), active players, and submarine statuses
- **FR-059**: Web UI MUST provide timeline/replay panel for scrubbing through travel_log entries (step-by-step playback)
- **FR-060**: Web UI MUST poll `/api/status` every 5 seconds or use WebSocket for real-time updates (global broadcasts, EMP hits, treasure pickup)

**MCP Tool Integration**

- **FR-061**: System MUST provide MCP (Model Context Protocol) server exposing tools that wrap OpenAPI endpoints: register_user, login_user, discover_field, surface, use_tool, exchange_frequency, broadcast_message, send_direct_message, get_status, get_game_state, get_messages, get_replay
- **FR-062**: Each MCP tool MUST accept structured input parameters matching the corresponding OpenAPI endpoint request schema and return responses in MCP tool result format
- **FR-063**: MCP tools MUST include player authentication context (session token) passed via MCP tool invocation metadata for authenticated endpoints
- **FR-064**: MCP tool responses MUST include human-readable summaries (e.g., "Discovered empty tile at (5,7). Oxygen: 18/20. Discoveries: 3/10.") alongside structured data for AI agent parsing
- **FR-065**: MCP tools MUST handle API errors gracefully and return error details in MCP error format with diagnostic context (operation, submarine_id, error_code, user-facing message)

**Data Persistence & State Management**

- **FR-066**: System MUST persist user accounts: username (unique), password_hash, created_at, last_login_at
- **FR-067**: System MUST persist all match state to a database: match_id, start_time, map_configuration (dimensions, treasure location, home_base positions), submarine states (all fields from FR-013), tile discovery history, message logs, event logs
- **FR-068**: System MUST maintain an in-memory cache of active match state for low-latency reads (current submarine positions, oxygen levels, statuses, known_fields)
- **FR-069**: System MUST write state updates to database asynchronously after in-memory updates (write-through cache pattern); critical state changes (treasure pickup, victory, EMP hits, inactivity timeouts) MUST be flushed synchronously
- **FR-070**: On server crash or restart, system MUST restore active match state from database and resume gameplay with last persisted submarine positions, oxygen levels, and match progress
- **FR-071**: System MUST persist completed matches (status=ended) for historical replay; include final state, winner submarine_id, match_duration, and full event timeline
- **FR-072**: System MUST support querying historical match data via API endpoint GET /api/matches/{match_id}/replay for post-game analysis and debugging

### Key Entities

- **Match**: Game session with unique match_id, start_time, end_time, status (active|ended), winner_username, map configuration, and collection of submarine states
- **User**: Account with unique username, password_hash, created_at, last_login_at; linked to submarine via username
- **Submarine**: Player's avatar with state (position, oxygen (0-20), status, inventory, treasure_held, disabled_count, frequency_secret, known_frequencies, known_fields, travel_log, cooldowns, messages)
- **Map**: 2D grid of tiles (MAX_X × MAX_Y) with per-tile content (empty, treasure, tool, hazard, home_base)
- **Tile**: Grid cell with coordinates (x,y) and content type; visibility per player via known_fields
- **Tool**: Collectible item (EMP, sonar, repair_kit, booster); single-use, stored in inventory
- **Message**: Communication record (from, to/channel, text, timestamp)
- **Event**: Travel log entry (x, y, timestamp, event type, details)

### Assumptions

- **Authentication**: Simple username/password authentication; users register once, login receives 24-hour session token (JWT or opaque); no email verification required; password recovery out of scope.
- **Server Architecture**: Backend uses persistent database (e.g., PostgreSQL, MongoDB) with in-memory cache layer (e.g., Redis) for active match state; provides durability for crash recovery and historical match replay while maintaining low-latency reads for real-time gameplay.
- **Tool Effects**: Tool types (sonar, repair_kit, booster) have predefined effects: sonar reveals adjacent tiles (with possible glitch), repair_kit restores oxygen (5 units), booster temporarily increases movement speed or range. Exact effects can be tuned during implementation.
- **Match Duration**: Matches are unbounded in time unless timeout or victory occurs; server can impose inactivity timeout for match reset.
- **Network Latency**: 10-second discover delay includes network round-trip; server enforces delay on completion, not on request.
- **WebSocket vs Polling**: Real-time updates can use WebSocket for push events (treasure pickup, EMP hits) with fallback to 5-second polling for status.
- **Grid Topology**: 4-neighbor adjacency (no diagonals); map is bounded rectangle (no wrapping/torus topology).
- **OpenTelemetry Integration**: System uses OpenTelemetry SDK for instrumentation; metrics/logs/traces exported to OTLP-compatible backend (e.g., Jaeger, Prometheus, Grafana stack); exact backend configuration is deployment-specific.
- **MCP Tool Architecture**: MCP server acts as a thin wrapper layer over OpenAPI endpoints; game logic resides in backend API; MCP tools translate between MCP protocol (JSON-RPC) and REST API calls; enables both human players (Web UI → API) and AI agents (MCP tools → API) with consistent behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New users can register and login within 5 seconds; duplicate username registration returns clear error; invalid login credentials return clear error
- **SC-002**: 20 authenticated players can simultaneously join a match, each spawning at a unique home_base, and begin exploration without server errors or collisions
- **SC-003**: A player completes a 10-discovery exploration cycle (discover 10 tiles, surface, resume) in under 5 minutes (including mandatory 10s per discovery and 60s surface time)
- **SC-004**: A player discovers the treasure, receives global broadcast within 1 second, navigates to home_base (average path length ~16 tiles for 32x32 map), and surfaces to win in under 10 minutes
- **SC-005**: Two players on the same tile exchange frequencies and send bidirectional direct messages successfully within 30 seconds of encounter
- **SC-006**: A player uses EMP tool 4 times on a treasure-carrying target within 2 minutes, forcing treasure drop, and the treasure becomes discoverable by any player within 10 seconds
- **SC-007**: Web UI loads player's fog-of-war map, status panel (including oxygen level), and message inbox in under 2 seconds and updates in real-time (or within 5-second polling interval) when events occur
- **SC-008**: System handles 20 concurrent players issuing discover actions simultaneously without timestamp conflicts (actions processed in order; no data corruption or lost actions)
- **SC-009**: 95% of discovery actions complete within 10 ± 0.5 seconds (server delay consistency)
- **SC-010**: Inactive player (10 minutes no action) is marked destroyed, treasure drops if held, and slot becomes available within 30 seconds of timeout
- **SC-011**: Match resets correctly after victory, with all submarines respawning and treasure relocated
- **SC-012**: Travel log replay allows players to scrub through 50+ logged events (positions + encounters) smoothly without UI lag or missing data
- **SC-013**: Distributed traces capture end-to-end request flows for all critical paths (register, login, discover, EMP, treasure pickup) with complete span hierarchy and <50ms instrumentation overhead
- **SC-014**: AI agents using MCP tools and human players using Web UI can participate in the same match simultaneously with identical gameplay mechanics and timing constraints
- **SC-015**: Server recovers from crash within 30 seconds, restoring active match state from database with all 20 players able to resume gameplay from last persisted positions and oxygen levels without data loss
