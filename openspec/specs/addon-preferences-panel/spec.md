## ADDED Requirements

### Requirement: Addon preferences class
The addon SHALL define an `AddonPreferences` class that extends `bpy.types.AddonPreferences` to store user-configurable settings.

#### Scenario: Preferences accessible in Blender UI
- **WHEN** user opens Edit > Preferences > Add-ons and selects the MCP addon
- **THEN** a preferences panel is displayed with configurable options

### Requirement: Socket server port configuration
The preferences SHALL include a configurable port number for the MCP socket server.

#### Scenario: Port property defined
- **WHEN** preferences are loaded
- **THEN** a port IntProperty is available with default value 9876

#### Scenario: Port value persisted
- **WHEN** user changes the port and restarts Blender
- **THEN** the configured port value is restored

### Requirement: Socket server host configuration
The preferences SHALL include a configurable host address for the socket server binding.

#### Scenario: Host property defined
- **WHEN** preferences are loaded
- **THEN** a host StringProperty is available with default value "127.0.0.1"

### Requirement: Auto-start socket server option
The preferences SHALL include an option to automatically start the socket server when the addon is enabled.

#### Scenario: Auto-start property defined
- **WHEN** preferences are loaded
- **THEN** an auto_start BoolProperty is available with default value False

#### Scenario: Auto-start behavior
- **WHEN** addon is registered and auto_start is True
- **THEN** the socket server starts automatically

### Requirement: Preferences UI layout
The preferences panel SHALL display settings in an organized layout with clear labels.

#### Scenario: UI shows server settings
- **WHEN** preferences panel is drawn
- **THEN** it shows: host, port, auto-start toggle, and current server status

#### Scenario: UI shows server status
- **WHEN** socket server is running
- **THEN** preferences panel indicates "Server running on {host}:{port}"

#### Scenario: UI shows server stopped
- **WHEN** socket server is not running
- **THEN** preferences panel indicates "Server stopped"
