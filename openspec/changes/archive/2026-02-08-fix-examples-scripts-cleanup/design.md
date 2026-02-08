## Context

The `examples/` and `scripts/` directories serve developers and CI. Three independent `sys.path` hack strategies exist, the compatibility-results writer diverged from the reader's JSON schema, CI has a duplicate job, and documentation drifted from reality.

Key current state:
- `compatibility-results.json` uses key `test_results` (ground truth)
- `check_compatibility.py` reads `test_results` — correct
- `run_real_blender_tests.py` writes `blender_versions` — incorrect (bug)
- `tests/_pathfix.py` provides a shared path-fix pattern; `examples/` and `scripts/` don't use it
- CI has two jobs (`compatibility` and `blender-compat`) doing the same work

## Goals / Non-Goals

**Goals:**
- Fix JSON key mismatch so writer output is consumable by reader
- Replace fragile string-counting with structured test output
- Eliminate CI duplication
- Unify `sys.path` resolution across `examples/` and `scripts/`
- Align README documentation with actual file state
- Remove dead code (`main.py`)

**Non-Goals:**
- Adding new example scripts (Example 2, 3) — separate capability work
- Adding CLI argument parsing to `stdio_loop.py` — out of scope
- Changing compatibility-results JSON schema beyond the key fix
- Modifying test logic in `tests/`

## Decisions

### D1: Align writer key to `test_results`

The existing `compatibility-results.json` and `check_compatibility.py` both use `test_results`. The writer is the outlier using `blender_versions`.

**Decision**: Change writer to use `test_results`. Also align internal variable names.

**Alternative**: Rename everything to `blender_versions`. Rejected — the checked-in data and reader already agree on `test_results`, so changing the writer is a single-point fix.

### D2: Use `pytest --junitxml` for structured parsing

**Decision**: Pass `--junitxml=<tmpfile>` to pytest in `run_real_blender_tests.py` and parse XML for test counts. JUnit XML is built into pytest with zero extra dependencies.

**Alternative**: `pytest-json-report`. Rejected — requires extra dependency while `--junitxml` is built-in.

### D3: Shared `_pathfix.py` per directory

**Decision**: Create `examples/_pathfix.py` and `scripts/_pathfix.py`, each following the `tests/_pathfix.py` pattern. Consumer files replace ad-hoc hacks with `import _pathfix`.

**Alternative**: Single root-level `_pathfix.py`. Rejected — different directories have different `parents[N]` depths; per-directory keeps logic trivial and local.

**Alternative**: Require `pip install -e .` everywhere. Rejected — scripts should remain runnable without install for quick iteration.

### D4: Remove redundant `compatibility` CI job

**Decision**: Delete `compatibility` job (ci.yml lines 92-107). `blender-compat` matrix job is a strict superset.

### D5: Delete `main.py`

**Decision**: Delete root `main.py`. It only prints "Hello" and is unreferenced by any entry point, CI step, or documentation. The documented entry point is `python -m examples.stdio_loop`.

### D6: Trim `examples/README.md` to reality

**Decision**: Remove Example 2 and 3 sections. Add note: "Additional examples will be added as capabilities are implemented."

**Alternative**: Mark as "Planned". Rejected — untracked "Planned" entries become stale.

## Risks / Trade-offs

- **D1 local cache** — Developers with locally-generated files using `blender_versions` key must re-run the test script. The checked-in file already uses the correct key, so no repo-level migration needed.
- **D2 XML parsing complexity** — JUnit XML adds ~15 lines of `xml.etree` parsing vs. 3 lines of string counting, but eliminates false positives entirely.
- **D3 path-fix duplication** — Three near-identical `_pathfix.py` files (tests, examples, scripts). Acceptable because each is 10 lines and self-contained; a shared root helper would need relative-path gymnastics.
- **D4 CI coverage gap** — None. `blender-compat` covers versions 4.2, 4.5, 5.0; the removed `compatibility` job only tested 4.2.
- **D5 entry point confusion** — If any external tool references `main.py`, it breaks. Mitigated by grep-searching for references before deletion.
