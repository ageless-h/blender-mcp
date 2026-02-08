# Scripts

Developer and maintenance scripts live here. Keep scripts small and documented.

## Compatibility Checks

- `python scripts/check_compatibility.py`
- Optional: set `BLENDER_VERSION` to validate support

## Real Blender Test Runner

- `python scripts/run_real_blender_tests.py`
- Runs integration tests against all configured Blender versions and aggregates results into `docs/versioning/compatibility-results.json`
- Configure Blender paths in `tests/blender-paths.json` or set `BLENDER_EXECUTABLE`

## Plugin Boundary Validation

- `python scripts/validate_plugin_boundary.py`
- Validates the addon plugin boundary contract by checking that required entrypoints exist in the implementation
