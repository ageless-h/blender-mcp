# JSON-RPC Parse Errors

## Purpose
TBD.

## Requirements

### Requirement: JSON-RPC parse errors are returned
The transport handler SHALL return JSON-RPC -32700 for invalid JSON payloads and record an audit event.

#### Scenario: Parse error
- **WHEN** an invalid JSON message is received
- **THEN** a -32700 error response is returned and audited
