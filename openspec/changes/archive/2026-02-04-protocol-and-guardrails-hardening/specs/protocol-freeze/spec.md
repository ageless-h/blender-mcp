## MODIFIED Requirements

### Requirement: Protocol semantics are frozen
The protocol SHALL be JSON-RPC 2.0 newline-delimited messages and MUST support minimal JSON-RPC fields.

#### Scenario: Protocol conformance
- **WHEN** a message is emitted
- **THEN** it is a JSON-RPC 2.0 object encoded as a single JSON line with required fields
