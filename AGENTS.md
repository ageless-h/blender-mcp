# AGENTS

## OVERVIEW

Blender MCP — MCP server for AI-assisted Blender automation. Python >=3.11, zero runtime deps. Two-process architecture: MCP server (PyPI `ageless-blender-mcp`) talks to Blender addon over TCP.

```
LLM Client ←MCP JSON-RPC→ blender_mcp (server) ←TCP socket→ blender_mcp_addon (Blender)
```

- **105 Python files**, **~17,500 lines**
- **29 tools**, **0 prompts** (tools-only server), **37 registered handlers** (across 29 files)
- **Blender**: 4.2 LTS / 4.5 LTS / 5.0+ / 5.1

## STRUCTURE

```
src/
  blender_mcp/              # MCP server (PyPI) — see src/blender_mcp/AGENTS.md
    mcp_protocol.py         # MCPServer: entry, 29 tools, JSON-RPC dispatch
    schemas/tools.py        # Tool schemas (WHAT/WHEN/NOT + annotations)
    adapters/               # SocketAdapter (TCP) + MockAdapter (testing)
    catalog/                # CapabilityCatalog — version-scoped registration
    security/               # Allowlist, Guardrails, RateLimiter, AuditLogger
    prompts/registry.py     # Empty prompt registry (prompts removed)
    versioning/             # Blender version compat checks
    telemetry.py            # Usage telemetry
  blender_mcp_addon/        # Blender addon (runs inside Blender)
    __init__.py             # bl_info registration
    capabilities/base.py    # 29-tool dispatcher + _push_undo_step()
    handlers/               # See src/blender_mcp_addon/handlers/AGENTS.md
      registry.py           # @HandlerRegistry.register decorator
      types.py              # DataType enum + DATA_TYPE_TO_COLLECTION
      response.py           # _ok(), _error(), not_found_error()
      base.py               # BaseHandler + GenericCollectionHandler (shared CRUD)
      shared.py             # create_mesh_primitive, link_data_to_scene
      data/                 # 30 files — one per bpy data type
      nodes/ animation/ sequencer/ constraints/ physics/ uv/ scene/
      importexport/ info/ operator/ script/
    server/                 # Socket server (op_log, timeouts)
    operators.py preferences.py ui.py
tests/                      # See tests/AGENTS.md
  conftest.py               # src/ on sys.path, MCP_ADAPTER=mock fixture
  addon/ tools/ integration/ mcp/
docs/                       # capabilities/, testing/, clients/, architecture/
scripts/                    # Build/release helpers + CI scripts (check_compatibility, ci_install_blender, ci_run_blender_tests, validate_boundary)
examples/                   # stdio_loop.py
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add a new MCP tool | `schemas/tools.py` → `catalog/` → addon handler → `tests/tools/` | 5-step flow, see blender_mcp/AGENTS.md |
| Fix a handler bug | `handlers/data/<type>_handler.py` | Check `DATA_TYPE_TO_COLLECTION` for collection names |
| Add a new data type handler | `handlers/data/` + `types.py` | `@HandlerRegistry.register` + `DataType` enum |
| Debug MCP protocol | `mcp_protocol.py` | MCPServer class, tool dispatch, security pipeline |
| Change tool schema | `schemas/tools.py` | `_tool()` helper, `TOOL_DEFINITIONS` list |
| Write tests | `tests/addon/` or `tests/tools/` | Both unittest and pytest work |
| Blender version compat | `versioning/` + `animation/__init__.py` | `iter_fcurves()` for 5.1 compat |
| Security/guardrails | `security/` (4 files) | Allowlist → Guardrails → RateLimiter → AuditLogger |

## ANTI-PATTERNS

- **Never** compute bpy.data collection name from `bl_rna.identifier.lower()+"s"` — use `DATA_TYPE_TO_COLLECTION`
- **Never** access `action.fcurves` directly — use `iter_fcurves(action)` from `animation/__init__.py` (Blender 5.0+ compat)
- **Never** skip `obj.data is not None` check before data property access (Empty objects)
- **Never** mutate original images — copy first, clean up in `finally`
- **Never** use dict positional arg for context overrides — use `temp_override()` (Blender 4.2+)
- **Never** set `hide_render` when toggling visibility — only `hide_viewport`
- **Never** import `blender_mcp_addon` from `blender_mcp` (separate processes)
- **Never** access `bpy.data.curves` without `_curves_available()` guard (Blender 5.0+ only)
- **Never** use `hasattr(sed, "strips")` to detect 5.0+ VSE API — Blender 4.5 also has `sed.strips` as an alias; check `bpy.app.version >= (5, 0)` instead
- **Never** use `frame_end=` in `new_effect()` for Blender 5.0+ VSE — use `length=` (frame_end - frame_start); see `_new_effect_kwargs()` in `sequencer/editor.py`

## CONVENTIONS

- Ruff: line-length 120, select E/F/W/I only (no N/flake8-bugbear)
- `from __future__ import annotations` in every non-__init__ source file
- Per-file ignores in `pyproject.toml` (E402 for mcp_protocol, E741 for core_handlers/nodes/reader)
- Response format: `_ok(result=..., started=t)` / `_error(code=..., message=..., started=t)` — never raw dicts
- Tool descriptions use WHAT/WHEN/NOT three-part pattern
- All addon writes trigger `_push_undo_step()` via `capabilities/base.py` dispatcher for Ctrl+Z
- Fractional FPS: `fps_base=1000` (handles 23.976)

## COMMANDS

```bash
uv sync                                                          # Install
uv run python -m unittest discover -s tests -p "test_*.py"       # Tests (CI uses this)
uv run pytest tests/                                             # Tests (also works — conftest uses pytest fixtures)
uv run ruff check src/ tests/                                    # Lint
uv run python -m examples.stdio_loop                             # Run stdio example
python scripts/ci_install_blender.py 4.2 linux-x64              # Download Blender for local testing
python scripts/ci_run_blender_tests.py /path/to/blender         # E2E tests with real Blender (run locally)
```

CI (`.github/workflows/ci.yml`): lint + unit (3.11/3.12/3.13) + coverage (≥75%). Blender integration tests run locally via `scripts/ci_run_blender_tests.py`, not in CI.

## BLENDER GUI CONTROL (macOS)

### Start/Stop Workflow

```bash
# Start Blender GUI
open -a Blender
sleep 3  # Wait for startup

# MCP operations via tools...

# Save and quit (via MCP)
blender_execute_operator(operator="wm.save_mainfile")      # Save current file
blender_execute_operator(operator="wm.save_as_mainfile", params={"filepath": "/path/to/file.blend"})  # Save as
blender_execute_operator(operator="wm.quit_blender")       # Quit (graceful, no confirmation dialog)

# Alternative: force quit (not recommended)
pkill -f "/Applications/Blender.app"
```

### Key Findings

| Operation | Method | Notes |
|-----------|--------|-------|
| Start GUI | `open -a Blender` | macOS only; wait 3s for startup |
| Save | `wm.save_mainfile` | Saves to current file path |
| Save As | `wm.save_as_mainfile` | Requires filepath param |
| Quit (graceful) | `wm.quit_blender` | No confirmation dialog, discards unsaved changes |
| Quit (force) | `pkill -f Blender` | Use only if graceful quit fails |
| Open file | `wm.open_mainfile` | Requires filepath param |

**Important**: `wm.quit_blender` does NOT prompt for unsaved changes. Always call save operators first if you want to preserve changes.
