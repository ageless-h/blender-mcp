## Why

The current addon is a contract-only stub and does not exercise real Blender execution via `bpy`, leaving core integration risk (performance, failure modes, and boundary behavior) unvalidated.
This change adds a small, real `bpy` PoC for 1–2 MVP capabilities to de-risk the plugin boundary and provide a concrete reference for contributors.

## What Changes

- Implement a real addon-side PoC for `scene.read` and `scene.write` using `bpy`.
- Add plugin-side validation of common error boundaries (invalid payloads, missing/invalid targets, and safe failure reporting).
- Add a plugin-side runnable example or test harness that can be executed in Blender (headless-friendly) to:
  - Exercise the PoC end-to-end
  - Record basic performance timings for the operations
  - Produce deterministic output suitable for CI/manual verification

## Capabilities

### New Capabilities
- (none)

### Modified Capabilities
- `plugin-boundary-poc`: Expand the PoC requirements from contract validation-only to a real `bpy` execution PoC covering `scene.read`/`scene.write`, including basic performance measurement and explicit error-boundary scenarios, with a runnable plugin-side example/test.

## Impact

- Affected areas:
  - `addon/`: new PoC implementation code and an execution harness entry (example/test)
  - `docs/`: update PoC documentation and how to run it (including headless usage)
  - `tests/` and/or `examples/`: add a plugin-side runnable scenario (depending on chosen harness)
- Dependencies / environment:
  - Running the PoC requires Blender with Python (`bpy`) available (LTS 3.6 and 4.x per contract).
- Risk:
  - Blender version differences may require small compatibility handling; failures should be explicit and deterministic.
