## ADDED Requirements

### Requirement: Start server operator
The addon SHALL provide a Blender operator `MCP_OT_start_server` to start the socket server.

#### Scenario: Operator registered
- **WHEN** addon is registered
- **THEN** the start server operator is available as `mcp.start_server`

#### Scenario: Operator starts server
- **WHEN** operator is invoked and server is not running
- **THEN** socket server starts on configured host:port and operator returns {'FINISHED'}

#### Scenario: Operator reports already running
- **WHEN** operator is invoked and server is already running
- **THEN** operator reports info message "Server already running" and returns {'CANCELLED'}

### Requirement: Stop server operator
The addon SHALL provide a Blender operator `MCP_OT_stop_server` to stop the socket server.

#### Scenario: Operator registered
- **WHEN** addon is registered
- **THEN** the stop server operator is available as `mcp.stop_server`

#### Scenario: Operator stops server
- **WHEN** operator is invoked and server is running
- **THEN** socket server stops cleanly and operator returns {'FINISHED'}

#### Scenario: Operator reports not running
- **WHEN** operator is invoked and server is not running
- **THEN** operator reports info message "Server not running" and returns {'CANCELLED'}

### Requirement: Server status tracking
The addon SHALL track server running state for UI feedback and operator logic.

#### Scenario: Status accessible globally
- **WHEN** operators or UI need server status
- **THEN** a module-level function `is_server_running()` returns current state

### Requirement: Operator UI integration
The operators SHALL be accessible from Blender's UI menus and preferences panel.

#### Scenario: Operators in preferences
- **WHEN** user views addon preferences
- **THEN** start/stop buttons are visible based on current server state

#### Scenario: Start button shown when stopped
- **WHEN** server is not running
- **THEN** preferences shows "Start Server" button

#### Scenario: Stop button shown when running
- **WHEN** server is running
- **THEN** preferences shows "Stop Server" button

### Requirement: Thread-safe server management
The socket server SHALL run in a background thread without blocking Blender's UI.

#### Scenario: Non-blocking start
- **WHEN** start operator is invoked
- **THEN** Blender UI remains responsive while server runs

#### Scenario: Clean shutdown
- **WHEN** stop operator is invoked or addon is unregistered
- **THEN** server thread terminates gracefully without hanging
