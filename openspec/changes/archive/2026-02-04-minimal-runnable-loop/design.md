## Context

The current MCP server scaffold lacks a real stdio transport path, a concrete audit logger, and an auditable allowlist update flow. These are required to make the system minimally runnable and verifiable.

## Goals / Non-Goals

**Goals:**
- Wire MCPServer to a real stdio transport for a minimal request/response loop.
- Provide a concrete audit logger implementation (memory + file/JSON export).
- Ensure allowlist updates generate audit events.
- Publish minimal entry documentation (README/AGENTS/project.md).
- Provide a runnable integration example and script.
- Add a time window to rate limiting.
- Implement a minimal addon stub that exposes a contract entrypoint.

**Non-Goals:**
- Implement full Blender capability coverage.
- Introduce network transports beyond stdio.
- Build production-grade observability beyond the audit logger.
- Provide a complete addon feature set.

## Decisions

- **Use stdio transport as the MVP path.**
  - Rationale: aligns with MCP defaults and enables a minimal runnable loop.
  - Alternatives: HTTP/WebSocket (deferred).

- **Provide two audit implementations: memory and JSON file export.**
  - Rationale: memory is fast for tests, JSON file supports persistence.
  - Alternatives: external logging backends (deferred).

- **Emit audit events on allowlist updates.**
  - Rationale: required by security guardrails and improves traceability.

- **Document a minimal runnable loop in README/AGENTS/project.md.**
  - Rationale: ensures new contributors can execute the minimal path.

- **Add a time-windowed rate limiter.**
  - Rationale: count-only limits are insufficient for time-based throttling.

## Risks / Trade-offs

- **stdio limits remote scenarios** -> Mitigation: keep transport adapter interface stable for future transports.
- **File-based audit logs can grow** -> Mitigation: keep basic implementation and document retention policy later.
- **Addon stub may diverge from future plugin design** -> Mitigation: keep it minimal and contract-focused.
