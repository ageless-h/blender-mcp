## MODIFIED Requirements

### Requirement: Minimal JSON-RPC 2.0 fields are enforced
The handler SHALL accept jsonrpc, method, params, id and return errors for invalid JSON payloads.

#### Scenario: Invalid JSON payload
- **WHEN** a request payload is not valid JSON
- **THEN** the server returns a -32700 error response
