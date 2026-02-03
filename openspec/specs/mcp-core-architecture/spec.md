# MCP Core Architecture

## Purpose
TBD.

## Requirements

### Requirement: MCP core defines stable service lifecycle
The MCP core SHALL define a stable service lifecycle with explicit initialization, readiness, shutdown, and error handling states.

#### Scenario: Normal startup and shutdown
- **WHEN** the MCP service starts
- **THEN** it transitions through initialization to ready state and exposes health status

#### Scenario: Error during initialization
- **WHEN** a critical dependency fails during initialization
- **THEN** the service reports a non-ready state and exits with a deterministic error code

### Requirement: Core separates protocol handling from Blender integration
The MCP core SHALL isolate protocol/transport handling from Blender-specific integration via an adapter boundary.

#### Scenario: Adapter substitution
- **WHEN** a Blender adapter is replaced with a mock adapter
- **THEN** MCP protocol handling remains unchanged and functional

### Requirement: Transport abstraction supports multiple deployment modes
The MCP core SHALL expose a transport-agnostic interface to allow different deployment modes without changing core logic.

#### Scenario: Alternate transport enabled
- **WHEN** a different transport adapter is configured
- **THEN** the core routes requests through the adapter without code changes
