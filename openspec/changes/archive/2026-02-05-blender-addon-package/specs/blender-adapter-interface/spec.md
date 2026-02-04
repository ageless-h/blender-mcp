## MODIFIED Requirements

### Requirement: Socket server location update
The SocketAdapter SHALL connect to the socket server provided by the new addon package at `src/blender_mcp_addon/`.

#### Scenario: Adapter connects to addon package server
- **WHEN** SocketAdapter is initialized
- **THEN** it connects to the socket server running from the installed Blender addon

### Requirement: Addon socket server uses new package structure
The addon socket server SHALL be integrated into the new package structure under `src/blender_mcp_addon/server/`.

#### Scenario: Server module location
- **WHEN** addon starts socket server
- **THEN** server code is loaded from `blender_mcp_addon.server` module

#### Scenario: Capability handlers from package
- **WHEN** socket server receives capability request
- **THEN** it routes to handlers in `blender_mcp_addon.capabilities` module

### Requirement: Import path compatibility
The addon package SHALL maintain the same `execute_capability()` contract for backward compatibility.

#### Scenario: Contract preserved
- **WHEN** socket server calls execute_capability
- **THEN** request/response format matches existing contract (ok, result, error, timing_ms)

#### Scenario: Handler signature unchanged
- **WHEN** capability handler is invoked
- **THEN** it receives (payload, started) and returns dict with ok/result/error/timing_ms
