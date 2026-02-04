# Blender Addon

## Scope
This directory contains the Blender addon implementation and its contract artifacts.

## PoC Harness

The addon includes a small `bpy` proof-of-concept harness at `addon/poc_harness.py`.

Run it in Blender (headless-friendly):

```bash
blender --background --factory-startup --python addon/poc_harness.py
```

The harness prints one JSON object per line and exercises:
- `scene.read` success
- `scene.write` success (with cleanup for repeatable runs)
- one representative invalid-params error case

## Verification Checklist

- Plugin boundary validation: `python scripts/validate_plugin_boundary.py`
- Unit/integration tests: `uv run python -m unittest discover -s tests -p "test_*.py"`
- Stdio example: `python -m examples.stdio_loop`

## Rules
- Keep addon code isolated from core service code in `src/`.
- Use the contract template in `contract.md` to document entrypoints and versioning.
