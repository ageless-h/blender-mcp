## Why

Current documentation diverges from implementation: rate-limits doc claims global guardrails, README omits JSON-RPC 2.0 framing, and AGENTS guidance lacks verification details. This creates confusion for contributors and breaks spec expectations.

## What Changes

- Align rate-limits documentation with implemented behavior (time-window only) or add minimal guardrail placeholder.
- Add minimal JSON-RPC 2.0 per-line framing note to README.
- Expand AGENTS guidance with verification steps and change-recording location.

## Capabilities

### New Capabilities
- `documentation-alignment`: Cross-doc consistency updates for minimal runnable guidance.

### Modified Capabilities
- `rate-limit-window`: Clarify documentation for windowed rate limiting.
- `agents-guidance`: Add verification and change-recording guidance.

## Impact

- Updates to docs/security/rate-limits.md, README.md, and AGENTS.md.
