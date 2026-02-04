## Context

JSON-RPC handling does not currently return parse errors, guardrails scope is not explicit, compatibility validation does not enforce required fields, plugin boundary validation is not in CI, and the minimal capability set is not registered by default.

## Goals / Non-Goals

**Goals:**
- Add JSON-RPC parse error handling with audit logging.
- Clarify and document guardrails scope (payload vs params).
- Validate compatibility result fields in check_compatibility.
- Add plugin boundary validation to CI.
- Register minimal capability set in startup/example flow.

**Non-Goals:**
- Replace the minimal JSON-RPC loop with full MCP SDK.
- Expand guardrails beyond payload/params scope.

## Decisions

- **Return JSON-RPC -32700 on parse errors and audit the event.**
  - Rationale: aligns with JSON-RPC spec and makes failures visible.

- **Define guardrails as payload-only (not params) for now.**
  - Rationale: minimal and consistent with current enforcement hooks.

- **Compatibility validation requires status and checked_at fields.**
  - Rationale: ensures results are meaningful.

- **CI includes plugin boundary validation step.**
  - Rationale: enforces contract on every change.

- **Minimal capability set is registered in example startup.**
  - Rationale: avoids empty catalog at runtime.

## Risks / Trade-offs

- **Guardrails scope limited to payload** → Mitigation: document future expansion to params.
