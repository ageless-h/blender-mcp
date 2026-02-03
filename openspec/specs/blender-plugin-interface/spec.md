# Blender Plugin Interface

## Purpose
TBD.

## Requirements

### Requirement: Defined plugin contract surface
The Blender integration SHALL expose a defined plugin contract surface for MCP to call into.

#### Scenario: Plugin contract discovery
- **WHEN** the MCP core initializes the Blender adapter
- **THEN** it validates the plugin contract version and required entry points

### Requirement: Versioned plugin API
The plugin interface SHALL be versioned to allow forward-compatible changes.

#### Scenario: Plugin API mismatch
- **WHEN** the plugin API version is unsupported
- **THEN** MCP refuses to activate the adapter and reports the incompatibility

### Requirement: Strict boundary between plugin and core
The plugin SHALL not access core internals beyond the defined contract surface.

#### Scenario: Out-of-contract access
- **WHEN** the plugin attempts to use non-contract APIs
- **THEN** the system denies access or fails fast with a clear error
