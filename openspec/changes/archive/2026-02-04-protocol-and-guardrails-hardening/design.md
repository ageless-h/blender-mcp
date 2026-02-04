## Context

Current implementation diverges from protocol and guardrail requirements: JSON-RPC 2.0 semantics are not enforced in transport handling, plugin boundary and compatibility scripts are missing, support matrix data is not enforced, and guardrails are not applied at request entry.

## Goals / Non-Goals

**Goals:**
- Implement minimal JSON-RPC 2.0 field handling in the stdio loop.
- Restore plugin boundary validation and compatibility execution scripts.
- Enforce support matrix data as part of compatibility checks.
- Ensure guardrails run before allowlist/permission checks.

**Non-Goals:**
- Full MCP SDK integration.
- Comprehensive Blender feature coverage.
- Complex resource enforcement beyond minimal guardrails.

## Decisions

- **Implement minimal JSON-RPC 2.0 handling in transport.**
  - Rationale: aligns behavior with protocol-freeze while keeping scope minimal.

- **Use scripts-based compatibility checks with JSON data files.**
  - Rationale: simple, testable, and CI-friendly.

- **Guardrails enforced at request entry.**
  - Rationale: ensures block before any capability execution.

## Risks / Trade-offs

- **Partial JSON-RPC support** → Mitigation: document supported fields and error cases.
- **Script-based checks rely on data freshness** → Mitigation: require updates per release.
