## Context

This change establishes a stable MCP service foundation for Blender that must prioritize security and reliability, remain maintainable long term, and support multiple Blender versions (LTS plus latest). The system must expose Blender capabilities to LLM agents via a controlled, testable interface, while reserving a clear plugin boundary for Blender-side integration. Reference implementations like ahujasid/blender-mcp and chrome-devtools-mcp inform structure and patterns, but the architecture must be generalized and hardened for long-term support.

## Goals / Non-Goals

**Goals:**
- Define a modular MCP server architecture with a strict security and stability model.
- Provide a Blender plugin interface contract with clear ownership boundaries.
- Establish a version compatibility policy aligned with Blender LTS and current releases.
- Specify a capability catalog and permission model for exposed Blender features.
- Define architectural evaluation gates and a test strategy for post-implementation validation.

**Non-Goals:**
- Implement every Blender capability in this design phase.
- Build Blender UI/UX features or user-facing tooling.
- Depend on private Blender APIs that cannot be maintained across versions.
- Finalize distribution or packaging strategy for all platforms.

## Decisions

- **Split MCP core from Blender integration via a plugin boundary.**
  - Rationale: decouples protocol handling, security, and capability management from Blender version specifics.
  - Alternatives: monolithic server embedded in Blender (rejected due to upgrade coupling and security surface).

- **Capability catalog with explicit schemas and permission scopes.**
  - Rationale: provides a stable contract for agents, enables allowlist control, and supports versioned expansion.
  - Alternatives: ad-hoc commands or implicit API exposure (rejected due to security and maintainability).

- **Security-first execution model with allowlists, sandboxing boundaries, rate limits, and audit logs.**
  - Rationale: addresses the primary requirement of stability and safety for agent-driven actions.
  - Alternatives: broad access with post-hoc monitoring (rejected as insufficiently safe).

- **Version compatibility layer with an explicit support matrix (LTS + latest).**
  - Rationale: ensures predictable behavior and controlled deprecation across Blender releases.
  - Alternatives: best-effort compatibility (rejected due to long-term maintenance needs).

- **Transport-agnostic MCP core with adapter interfaces.**
  - Rationale: preserves MCP protocol conformity while allowing different deployment modes.
  - Alternatives: single transport hard-coded (rejected due to limited deployment flexibility).

- **Architecture evaluation checkpoints before broad capability expansion.**
  - Rationale: validates the system can meet stability/security goals before scaling feature coverage.
  - Alternatives: implement-first, evaluate-later (rejected due to risk of foundational flaws).

- **Multi-version test harness with scenario-based integration tests.**
  - Rationale: guarantees behavior across supported Blender versions and validates real workflows.
  - Alternatives: unit tests only (rejected as insufficient for integration reliability).

## Risks / Trade-offs

- **Stricter security limits may reduce agent flexibility** -> Provide clear error surfaces and a staged allowlist expansion plan.
- **Multi-version support increases maintenance cost** -> Prioritize LTS coverage and automate compatibility testing.
- **Plugin boundary can limit access to internal Blender features** -> Document extension points and review feasibility per capability.
- **Transport abstraction adds complexity** -> Keep a minimal core interface and validate with one primary transport first.
- **Extensive test matrix can slow delivery** -> Start with critical workflows and expand coverage iteratively.
