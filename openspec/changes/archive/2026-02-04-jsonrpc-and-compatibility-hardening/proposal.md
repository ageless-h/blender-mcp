## Why

The current JSON-RPC handling and compatibility checks are functional but not robust: parse errors are not surfaced as JSON-RPC errors, guardrails scope is unclear, compatibility result validation is shallow, plugin boundary validation is not in CI, and the minimal capability set is not registered by default.

## What Changes

- Add JSON-RPC parse error handling and audit logging for invalid requests.
- Clarify guardrails scope (payload-only vs params-level) and align docs/behavior.
- Strengthen compatibility checks by validating required result fields.
- Add plugin boundary validation step to CI.
- Register the minimal capability set in example/startup flow.

## Capabilities

### New Capabilities
- `jsonrpc-parse-errors`: JSON-RPC -32700 handling and auditing.
- `compatibility-results-validation`: Validate required compatibility result fields.
- `plugin-boundary-ci`: Enforce plugin boundary validation in CI.
- `minimum-capability-registration`: Ensure minimal capability set is registered on startup.

### Modified Capabilities
- `resource-guardrails-strategy`: Clarify guardrails scope and enforcement details.
- `jsonrpc-minimal-handling`: Extend JSON-RPC handling with parse error response.

## Impact

- MCPServer transport handling, CI workflow, compatibility scripts, and example initialization may change.
- Documentation and tests will be updated to reflect the hardened behavior.
