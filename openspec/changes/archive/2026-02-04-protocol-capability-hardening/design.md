## Context

The project has a minimal runnable loop but lacks frozen protocol semantics, standardized audit schema, a defined minimum capability/permission set, validated plugin boundary, executable version compatibility checks, and resource guardrails. These gaps prevent safe expansion.

## Goals / Non-Goals

**Goals:**
- Freeze protocol semantics and message framing requirements.
- Standardize audit event schema and required fields.
- Define the minimal capability/permission catalog for MVP.
- Validate plugin boundary with a minimal PoC.
- Establish executable version compatibility checks and release gating.
- Define resource guardrails strategy and minimal enforcement hooks.

**Non-Goals:**
- Full MCP SDK integration beyond the minimal protocol semantics.
- Comprehensive Blender capability coverage.
- Production-grade resource enforcement across all runtimes.

## Decisions

- **Document protocol semantics as JSON-RPC 2.0 newline-delimited messages.**
  - Rationale: matches current minimal loop and provides a clear frozen contract.

- **Audit schema includes required fields plus optional metadata.**
  - Rationale: supports allowlist and capability audit without multiple event types.

- **Minimum capability set is explicit and small.**
  - Rationale: enables secure MVP scope with clear permissions.

- **Plugin boundary PoC uses addon entrypoint validation.**
  - Rationale: validates contract requirements with minimal complexity.

- **Compatibility checks run as part of CI gating.**
  - Rationale: makes version support enforceable.

- **Guardrails start as documented policy + minimal hooks.**
  - Rationale: avoids unimplemented claims while enabling future enforcement.

## Risks / Trade-offs

- **Frozen protocol may limit future evolution** → Mitigation: versioned protocol notes and follow-up change for SDK adoption.
- **Minimum capability list may omit needed workflows** → Mitigation: add expansion process in future change.
- **Guardrails placeholders may be misread as full enforcement** → Mitigation: explicit documentation of scope.
