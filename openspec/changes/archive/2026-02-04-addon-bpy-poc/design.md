## Context

- The current addon implementation is a minimal readiness stub (`addon_entrypoint`) and does not call into Blender via `bpy`.
- Existing boundary validation only checks that required entrypoints exist (see `scripts/validate_plugin_boundary.py`).
- The repo already defines the minimal capability names `scene.read` and `scene.write`, but there is no plugin-side execution path for them.
- The plugin boundary rules are:
  - Core owns protocol/security/dispatch.
  - Plugin owns Blender execution and all `bpy` interaction.

This change implements a small plugin-side PoC that can be executed inside Blender (preferably headless-friendly) to validate:
- Real `bpy` interaction for `scene.read` and `scene.write`
- Basic performance characteristics
- Deterministic error handling at the plugin boundary

## Goals / Non-Goals

**Goals:**
- Provide addon-side functions that implement `scene.read` and `scene.write` using `bpy`.
- Provide a runnable plugin-side harness (example/test) that:
  - Calls the PoC functions
  - Prints deterministic, machine-readable results (e.g., JSON) including timing
  - Exercises success and representative failure cases
- Keep the contract forward-compatible by extending (not breaking) existing addon entrypoint expectations.

**Non-Goals:**
- Full MCP protocol integration inside Blender.
- Implementing a complete capability registry/dispatcher inside the addon beyond what is needed for the PoC.
- Comprehensive cross-version compatibility layer; only minimal shims as needed for Blender 3.6 LTS and 4.x.

## Decisions

- Contract surface in addon:
  - Keep `addon_entrypoint()` unchanged to preserve existing validation.
  - Add a single new entrypoint (e.g., `execute_capability(request: dict) -> dict`) used by the harness to route `scene.read` / `scene.write`.
  - Rationale: one dispatcher entrypoint avoids contract explosion while still demonstrating how core could call into the addon later.

- Payload / result shape:
  - Use a JSON-serializable dict contract for requests and responses.
  - Response always includes:
    - `ok: bool`
    - `result: dict | None`
    - `error: {"code": str, "message": str, "data": dict | None} | None`
    - `timing_ms: float` (measured inside addon for the operation)
  - Rationale: deterministic, easy to validate in tests/CI logs, and compatible with transport layers.

- Error boundaries:
  - Validate request shape before touching `bpy`.
  - Catch exceptions from `bpy` operations and map them into stable `error.code` values (no raw tracebacks as the primary signal).
  - Rationale: boundary should fail safely and predictably.

- PoC semantics:
  - `scene.read`: return a minimal snapshot sufficient to prove real access (e.g., active scene name, object count, selected object names).
  - `scene.write`: perform a small deterministic mutation (e.g., create a uniquely-named cube or toggle an object property), and optionally clean up to keep repeated runs stable.
  - Rationale: observable effect while keeping runs repeatable.

- Harness location:
  - Prefer a Blender-executable example under `addon/` (or `examples/` if it can reliably run Blender) that can be invoked in headless mode.
  - Rationale: makes the PoC runnable without requiring core protocol wiring.

## Risks / Trade-offs

- Blender version drift (3.6 vs 4.x) may affect operators/data APIs.
  - Mitigation: prefer stable data API (`bpy.data`, `bpy.context.scene`) over fragile operators where possible; document any version-specific branches.

- Headless execution differences across platforms.
  - Mitigation: keep harness minimal, avoid UI-dependent operations, and document a recommended invocation command.

- Determinism of write operations (scene may not be empty).
  - Mitigation: write operations should use a unique name prefix and avoid destructive edits unless explicitly requested; optionally clean up created objects.

- Performance measurements may be noisy.
  - Mitigation: report coarse timings (single operation, ms) and treat them as indicative rather than strict benchmarks.
