## ADDED Requirements

### Requirement: BlenderAdapter protocol definition
The system SHALL define a `BlenderAdapter` protocol with an `execute(capability: str, payload: dict) -> AdapterResult` method that abstracts communication with the Blender addon process.

#### Scenario: Adapter protocol is injectable
- **WHEN** MCPServer is constructed
- **THEN** it accepts an optional BlenderAdapter instance for capability execution

#### Scenario: Adapter protocol defines execute method
- **WHEN** a capability request passes security checks
- **THEN** the adapter's execute method can be called with capability name and payload

### Requirement: Socket-based adapter implementation
The system SHALL provide a `SocketAdapter` implementation that communicates with the Blender addon over localhost TCP socket.

#### Scenario: Socket connection to addon
- **WHEN** SocketAdapter is initialized with host and port
- **THEN** it connects to the Blender addon's socket server

#### Scenario: Request-response over socket
- **WHEN** execute is called with capability and payload
- **THEN** adapter sends JSON request over socket and returns parsed JSON response

#### Scenario: Connection failure handling
- **WHEN** socket connection fails or times out
- **THEN** adapter returns AdapterResult with ok=False and error="adapter_unavailable"

### Requirement: Mock adapter for testing
The system SHALL provide a `MockAdapter` implementation that returns configurable responses without requiring Blender.

#### Scenario: Mock adapter in tests
- **WHEN** MockAdapter is configured with expected responses
- **THEN** execute returns the configured response for matching capability

#### Scenario: Mock adapter default behavior
- **WHEN** MockAdapter receives unregistered capability
- **THEN** it returns AdapterResult with ok=True and empty result

### Requirement: Addon socket server entrypoint
The Blender addon SHALL expose a socket server that listens for capability execution requests.

#### Scenario: Addon starts socket server
- **WHEN** addon socket server is started with port configuration
- **THEN** it listens for incoming TCP connections on localhost

#### Scenario: Addon processes capability request
- **WHEN** addon receives JSON request with capability and payload
- **THEN** it calls execute_capability and returns JSON response

### Requirement: Adapter result structure
AdapterResult SHALL contain fields: ok (bool), result (dict|None), error (str|None), timing_ms (float|None).

#### Scenario: Successful adapter result
- **WHEN** addon execution succeeds
- **THEN** AdapterResult has ok=True, result contains execution data, error is None

#### Scenario: Failed adapter result
- **WHEN** addon execution fails
- **THEN** AdapterResult has ok=False, result is None, error contains error code

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
