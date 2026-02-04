# Resource Guardrails

## Scope
Guardrails cover memory usage and long-running tasks.

## Strategy
- Start with minimal enforcement hooks in the core request path.
- Expand to real enforcement as measurements and thresholds are defined.

## Current Status
- Hooks enforce payload size and key-count limits, and allow capability blocking.

## Configuration
- `MCP_MAX_PAYLOAD_BYTES`
- `MCP_MAX_PAYLOAD_KEYS`
- `MCP_BLOCKED_CAPABILITIES` (comma-separated)
