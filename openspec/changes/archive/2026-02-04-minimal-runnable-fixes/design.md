## Context

The minimal runnable loop implementation diverges from the documented specs: CI workflow is missing, allowlist audit lacks update details, addon contract is not populated, rate-limit window behavior lacks tests, and protocol documentation does not match the current JSON-loop implementation.

## Goals / Non-Goals

**Goals:**
- Restore a minimal CI workflow for lint/unit/integration placeholder.
- Extend audit events to include update details for allowlist changes.
- Populate addon contract with the real entrypoint and version.
- Add tests covering time-window rate limiting behavior.
- Align protocol documentation or implementation.

**Non-Goals:**
- Introduce new transports beyond existing minimal stdio path.
- Expand addon functionality beyond a minimal entrypoint.
- Implement full MCP SDK integration if we choose to document the minimal loop instead.

## Decisions

- **Keep minimal JSON-loop implementation and update documentation accordingly.**
  - Rationale: fastest path to align docs with current behavior.
  - Alternative: migrate to official MCP SDK (deferred to a future change).

- **Audit event details stored in a generic metadata field.**
  - Rationale: simple schema that supports allowlist update details without new event types.

- **Rate-limit window behavior verified via unit/integration test.**
  - Rationale: ensures spec compliance with minimal scope.

## Risks / Trade-offs

- **Protocol alignment via docs risks future divergence** -> Mitigation: track SDK migration as a follow-up change.
- **Audit metadata is untyped** -> Mitigation: document expected fields for allowlist updates.
