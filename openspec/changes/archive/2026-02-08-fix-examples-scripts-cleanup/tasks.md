## 1. Fix P0 Bug: JSON Key Mismatch

- [x] 1.1 In `scripts/run_real_blender_tests.py`, change `blender_versions` key to `test_results` in the results dict built by `main()`
- [x] 1.2 In `scripts/run_real_blender_tests.py`, update `load_existing_results()` default dict to use `test_results` instead of `blender_versions`
- [x] 1.3 In `scripts/run_real_blender_tests.py`, update the `existing_by_version` map construction to read from `test_results`
- [x] 1.4 Verify `docs/versioning/compatibility-results.json` already uses `test_results` (no file change needed)

## 2. Replace Fragile Test Output Parsing

- [x] 2.1 In `run_real_blender_tests.py`, add `--junitxml` argument to the pytest subprocess call with a temporary file path
- [x] 2.2 Add `xml.etree.ElementTree` parsing logic to extract test counts from JUnit XML
- [x] 2.3 Remove the `output.count("PASSED")` / `output.count("FAILED")` string counting logic
- [x] 2.4 Clean up the temporary XML file after parsing

## 3. Clean Up Duplicate Imports

- [x] 3.1 In `run_real_blender_tests.py`, remove the duplicate `import sys` and `from pathlib import Path` inside `main()`
- [x] 3.2 In `run_real_blender_tests.py`, remove the duplicate `project_root` / `sys.path.insert` inside `main()` and use the top-level `PROJECT_ROOT`

## 4. Create Shared Path Fix Modules

- [x] 4.1 Create `examples/_pathfix.py` following the `tests/_pathfix.py` pattern
- [x] 4.2 Create `scripts/_pathfix.py` following the `tests/_pathfix.py` pattern
- [x] 4.3 In `examples/stdio_loop.py`, replace inline `sys.path` hack with `import _pathfix`
- [x] 4.4 In `scripts/validate_plugin_boundary.py`, replace try/except import hack with `import _pathfix`
- [x] 4.5 In `scripts/run_real_blender_tests.py`, remove the `sys.path.insert` in `main()` (already uses top-level `PROJECT_ROOT`)

## 5. Remove Dead Code

- [x] 5.1 Grep for references to `main.py` across the repo to confirm it is unreferenced
- [x] 5.2 Delete root `main.py`

## 6. Fix Documentation

- [x] 6.1 In `examples/README.md`, remove Example 2 and Example 3 sections; add note about future examples
- [x] 6.2 In `scripts/README.md`, add entries for `run_real_blender_tests.py` and `validate_plugin_boundary.py`

## 7. Deduplicate CI

- [x] 7.1 In `.github/workflows/ci.yml`, remove the `compatibility` job (lines 92-107)

## 8. Verification

- [x] 8.1 Run unit tests: `uv run python -m unittest discover -s tests -p "test_*.py"`
- [x] 8.2 Run the stdio example: `python -m examples.stdio_loop < /dev/null`
- [x] 8.3 Run `python scripts/validate_plugin_boundary.py` to confirm it still works
- [x] 8.4 Run `python scripts/check_compatibility.py` to confirm it still reads results correctly
