## ADDED Requirements

### Requirement: MCPServer uses stdio transport
The MCPServer SHALL support a real stdio transport for request/response handling.

#### Scenario: Stdio transport enabled
- **WHEN** the server is started with stdio transport
- **THEN** it accepts requests and produces responses over stdio

### Requirement: Transport adheres to adapter interface
The stdio transport SHALL implement the transport adapter interface.

#### Scenario: Transport adapter integration
- **WHEN** the transport is injected into the server
- **THEN** the server can send and receive messages through the adapter
