## 1. Addon contract and entrypoints

- [x] 1.1 Update `addon/contract.md` to document the new PoC entrypoint(s) (keep `addon_entrypoint` unchanged)
- [x] 1.2 Implement addon-side dispatcher entrypoint (e.g., `execute_capability(request: dict) -> dict`) in `addon/entrypoint.py`
- [x] 1.3 Implement `scene.read` PoC using `bpy` and return a deterministic scene snapshot
- [x] 1.4 Implement `scene.write` PoC using `bpy` with deterministic mutation and optional cleanup for repeatable runs
- [x] 1.5 Add request validation and stable error mapping (`error.code`, `error.message`, optional `error.data`) for invalid requests and `bpy` failures
- [x] 1.6 Add timing measurement (`timing_ms`) for each operation and ensure outputs are JSON-serializable

## 2. Runnable harness (headless-friendly)

- [x] 2.1 Add a Blender-executable harness script for the PoC that calls the addon entrypoint(s)
- [x] 2.2 Ensure the harness prints deterministic, machine-readable output (JSON) for:
  - `scene.read` success
  - `scene.write` success
  - at least one representative error case
- [x] 2.3 Document the recommended Blender invocation command (including headless mode) to run the harness

## 3. Repository integration and documentation

- [x] 3.1 Add or update repository documentation pointing to the PoC purpose, what it validates, and how to run it
- [x] 3.2 Decide and implement where the harness lives long-term (`addon/`, `examples/`, or `tests/`) and ensure it follows directory boundary rules
- [x] 3.3 Add a minimal CI/manual verification checklist for supported Blender versions (3.6 LTS and 4.x)

## 4. Verification

- [x] 4.1 Run plugin boundary validation: `python scripts/validate_plugin_boundary.py`
- [x] 4.2 Run unit/integration tests: `uv run python -m unittest discover -s tests -p "test_*.py"`
- [x] 4.3 Run stdio example loop: `python -m examples.stdio_loop`
- [x] 4.4 Execute the Blender harness locally and confirm all scenarios in the delta spec are covered (read/write/error/timing)
