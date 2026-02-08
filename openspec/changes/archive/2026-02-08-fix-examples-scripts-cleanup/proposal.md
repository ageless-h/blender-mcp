## Why

The `examples/` and `scripts/` directories have accumulated inconsistencies, a data-format bug, fragile patterns, and stale documentation that erode developer trust and CI reliability. A focused cleanup now prevents these issues from compounding as the project adds more capabilities.

## What Changes

- **Fix JSON key mismatch (bug)**: `check_compatibility.py` reads `test_results` but `run_real_blender_tests.py` writes `blender_versions`. Align both to a single key.
- **Replace fragile test-output parsing**: `run_real_blender_tests.py` counts occurrences of the string "PASSED"/"FAILED" in pytest stdout. Switch to structured output (e.g., `--junitxml` or `--json-report`).
- **Deduplicate CI jobs**: The `compatibility` job in `ci.yml` duplicates the `blender-compat` matrix job. Remove the redundant one.
- **Unify `sys.path` strategy**: Three files use three different path-hack patterns. Standardise on a single shared `_pathfix.py` helper (matching the pattern already used by `tests/`), or eliminate hacks entirely via editable install.
- **Remove phantom examples from README**: `examples/README.md` lists Example 2 and Example 3, which have no corresponding files. Remove the phantom entries (or mark as planned).
- **Remove dead `main.py`**: Root `main.py` only prints "Hello" and is unused by any entry point or CI step. Remove it or wire it to `run_stdio_loop`.
- **Complete `scripts/README.md`**: Document all three scripts, not just `check_compatibility.py`.
- **Clean up duplicate imports**: `run_real_blender_tests.py` re-imports `sys` and `Path` inside `main()` despite top-level imports.

## Capabilities

### New Capabilities

_(none — this change is a quality/hygiene cleanup with no new user-facing capabilities)_

### Modified Capabilities

- `compatibility-results-validation`: The results JSON schema changes — the canonical key for per-version entries must be explicitly defined and consistent between writer (`run_real_blender_tests.py`) and reader (`check_compatibility.py`).
- `validation-gate-ci`: CI workflow is modified — the redundant `compatibility` job is removed; the `blender-compat` matrix job becomes the single source of truth for compatibility gating.
- `runnable-examples`: The examples README is corrected to only list actually-existing examples; the path-resolution strategy for examples is standardised.
- `packaging-configuration`: If the cleanup adds a `[project.scripts]` entry point or shared `_pathfix.py`, the packaging spec gains a new requirement.
- `code-layout-conventions`: The unified import strategy (no ad-hoc `sys.path` hacks) becomes a documented convention.

## Impact

- **Files modified**: `scripts/check_compatibility.py`, `scripts/run_real_blender_tests.py`, `scripts/validate_plugin_boundary.py`, `scripts/README.md`, `examples/stdio_loop.py`, `examples/README.md`, `.github/workflows/ci.yml`, `main.py` (delete or replace)
- **Data format**: The compatibility-results JSON key rename is a **one-time migration** — any locally cached `compatibility-results.json` using the old key will need regeneration.
- **CI**: Removing the `compatibility` job reduces CI runtime; no new jobs added.
- **Dependencies**: No new external dependencies.
