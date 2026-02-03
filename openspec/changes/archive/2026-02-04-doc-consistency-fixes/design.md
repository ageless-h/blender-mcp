## Context

Documentation currently diverges from implementation: rate-limits docs reference global guardrails that are not implemented, README omits JSON-RPC 2.0 per-line framing, and AGENTS guidance lacks verification steps expected by the spec.

## Goals / Non-Goals

**Goals:**
- Align docs with current implementation and specs.
- Add minimal protocol framing note to README.
- Expand AGENTS guidance with verification and change-recording locations.

**Non-Goals:**
- Implement new runtime guardrails or protocol changes.
- Introduce new dependencies or tooling.

## Decisions

- **Remove or clarify global guardrails in rate-limits docs.**
  - Rationale: keep docs consistent with actual implementation.

- **Document JSON-RPC 2.0 per-line framing in README.**
  - Rationale: ensure users understand the minimal protocol contract.

- **Add verification steps to AGENTS guidance.**
  - Rationale: align with agents-guidance spec expectations.

## Risks / Trade-offs

- **Reduced visibility of future guardrails** -> Mitigation: note as future work in docs if needed.
