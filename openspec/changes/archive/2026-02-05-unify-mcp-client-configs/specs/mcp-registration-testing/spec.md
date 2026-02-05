## ADDED Requirements

### Requirement: MCP registration test module
The system SHALL provide a test module at `tests/mcp/test_registration.py` that validates MCP protocol registration functionality.

#### Scenario: Test file location
- **WHEN** running MCP registration tests
- **THEN** the test file SHALL be located at `tests/mcp/test_registration.py`

### Requirement: Initialize request validation
The test suite SHALL validate that the MCP server responds correctly to `initialize` requests.

#### Scenario: Initialize returns server info
- **WHEN** sending a JSON-RPC `initialize` request
- **THEN** the response SHALL contain `serverInfo` with `name` and `version` fields

#### Scenario: Initialize returns capabilities
- **WHEN** sending a JSON-RPC `initialize` request
- **THEN** the response SHALL contain `capabilities` object listing supported features

#### Scenario: Initialize response format
- **WHEN** receiving the `initialize` response
- **THEN** it SHALL be a valid JSON-RPC 2.0 response with matching `id` field

### Requirement: Tools list validation
The test suite SHALL validate that the MCP server responds correctly to `tools/list` requests.

#### Scenario: Tools list returns non-empty array
- **WHEN** sending a `tools/list` request after initialization
- **THEN** the response SHALL contain a non-empty `tools` array

#### Scenario: Each tool has required fields
- **WHEN** examining tools in the `tools/list` response
- **THEN** each tool SHALL have `name` and `description` fields

#### Scenario: Core tools are present
- **WHEN** examining the `tools/list` response
- **THEN** it SHALL include the core tools: `data.create`, `data.read`, `data.write`, `data.delete`, `data.list`, `data.link`, `operator.execute`, `info.query`

### Requirement: Test uses subprocess execution
The test SHALL use subprocess to invoke the MCP protocol module, simulating real client behavior.

#### Scenario: Subprocess invocation
- **WHEN** running the registration test
- **THEN** it SHALL spawn `python -m blender_mcp.mcp_protocol` as a subprocess

#### Scenario: Mock adapter for testing
- **WHEN** running tests without Blender
- **THEN** the test SHALL use `MCP_ADAPTER=mock` environment variable

### Requirement: JSON-RPC 2.0 compliance validation
The test suite SHALL validate that all responses conform to JSON-RPC 2.0 specification.

#### Scenario: Response has jsonrpc field
- **WHEN** receiving any response
- **THEN** it SHALL contain `"jsonrpc": "2.0"`

#### Scenario: Response has id field
- **WHEN** sending a request with an `id`
- **THEN** the response SHALL contain the same `id` value

#### Scenario: Error responses have error object
- **WHEN** the server returns an error
- **THEN** the response SHALL contain an `error` object with `code` and `message` fields

