# Stdio Transport

## Purpose
TBD.

## Requirements

### Requirement: MCPServer uses stdio transport
The MCPServer SHALL support a real stdio transport for request/response handling. The server SHALL verify adapter availability before accepting client requests.

#### Scenario: Stdio transport enabled
- **WHEN** the server is started with stdio transport
- **THEN** it accepts requests and produces responses over stdio

#### Scenario: Adapter readiness check before accepting requests
- **WHEN** server starts with BlenderAdapter configured
- **THEN** server attempts adapter connection before entering ready state

#### Scenario: Server reports adapter unavailable
- **WHEN** adapter connection fails during startup
- **THEN** server health reports state="error" with error_code="adapter_unavailable"

### Requirement: Transport adheres to adapter interface
The stdio transport SHALL implement the transport adapter interface.

#### Scenario: Transport adapter integration
- **WHEN** the transport is injected into the server
- **THEN** the server can send and receive messages through the adapter
