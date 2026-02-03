## Why

Minimal runnable loop still violates key specs: CI workflow is missing, allowlist audit lacks detail fields, addon contract is a template, rate-limit window tests are missing, and protocol implementation diverges from docs. These gaps block a stable verification loop.

## What Changes

- Restore minimal CI workflow to satisfy validation-gate-ci.
- Extend audit events with update details and align allowlist audit behavior.
- Populate addon contract with real entrypoint and version.
- Add time-window rate limit tests.
- Decide protocol direction: update docs to allow minimal JSON loop or migrate to official MCP SDK.

## Capabilities

### New Capabilities
- `protocol-alignment`: Align protocol implementation and documentation.

### Modified Capabilities
- `validation-gate-ci`: Restore minimal CI workflow compliance.
- `allowlist-audit`: Include update details in audit events.
- `audit-logger-implementation`: Support audit metadata fields.
- `addon-minimal-implementation`: Ensure contract reflects actual entrypoint.
- `rate-limit-window`: Add tests covering window reset behavior.

## Impact

- CI and tests will be adjusted.
- Audit event structure and allowlist update logic will change.
- Addon contract file will be updated.
- Protocol documentation or implementation will be aligned.
