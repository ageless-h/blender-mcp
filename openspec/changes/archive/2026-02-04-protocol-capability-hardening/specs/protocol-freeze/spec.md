## ADDED Requirements

### Requirement: Protocol semantics are frozen
The protocol SHALL be defined as JSON-RPC 2.0 messages, newline-delimited, UTF-8 encoded.

#### Scenario: Protocol conformance
- **WHEN** a message is emitted
- **THEN** it is a JSON-RPC 2.0 object encoded as a single JSON line
