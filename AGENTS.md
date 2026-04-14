# AGENTS

**Generated:** 2026-04-14
**Commit:** cbe66f5
**Branch:** master

## OVERVIEW

Blender MCP — MCP server integration for AI-assisted Blender automation. Python >=3.11, zero runtime deps. Two-process architecture: MCP server (PyPI `ageless-blender-mcp` v1.2.0) talks to Blender addon over TCP.

```
LLM Client ←MCP JSON-RPC→ blender_mcp (server) ←TCP socket→ blender_mcp_addon (Blender)
```

- **154 Python files**, **22,606 lines**, max depth 7
- **26 tools**, **10 prompts**, **37 registered handlers**
- **Blender**: 4.2 LTS / 4.5 LTS / 5.0+ / 5.1

## STRUCTURE

```
src/
  blender_mcp/              # MCP server (PyPI) → AGENTS.md
    mcp_protocol.py         # MCPServer: entry, 26 tools, 10 prompts, JSON-RPC dispatch
    schemas/tools.py        # 1480-line tool schemas (WHAT/WHEN/NOT + annotations)
    adapters/               # SocketAdapter (TCP) + MockAdapter (testing)
    catalog/                # CapabilityCatalog — version-scoped registration
    security/               # Allowlist, Guardrails, RateLimiter, AuditLogger
    prompts/registry.py     # 10 prompts (7 workflow + 3 strategy)
    versioning/             # Blender version compat checks
  blender_mcp_addon/        # Blender addon (runs inside Blender)
    __init__.py             # bl_info registration
    capabilities/base.py    # 26-tool dispatcher (659 lines)
    handlers/               # → AGENTS.md
      registry.py           # @HandlerRegistry.register decorator
      types.py              # DataType enum + DATA_TYPE_TO_COLLECTION
      response.py           # _ok(), _error(), not_found_error()
      data/                 # 30 handler files for bpy data types
      nodes/ animation/ sequencer/ constraints/ physics/ uv/ scene/ ...
    server/                 # Socket server (op_log, timeouts)
    operators.py preferences.py ui.py
tests/                      # → AGENTS.md
  conftest.py               # MCP_ADAPTER=mock, src/ on sys.path
  addon/ tools/ integration/ mcp/
docs/                       # capabilities/, testing/, clients/, architecture/
scripts/                    # Build/release helpers
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
| Write tests | `tests/addon/` or `tests/tools/` | unittest (NOT pytest), `MCP_ADAPTER=mock` |
| Blender version compat | `versioning/` + `animation/__init__.py` | `iter_fcurves()` for 5.1 compat |
| Security/guardrails | `security/` (4 files) | Allowlist → Guardrails → RateLimiter → AuditLogger |

## ANTI-PATTERNS (THIS PROJECT)

- **Never** compute bpy.data collection name from `bl_rna.identifier.lower()+"s"` — use `DATA_TYPE_TO_COLLECTION`
- **Never** access `action.fcurves` directly — use `iter_fcurves(action)` from `animation/__init__.py` (Blender 5.1 compat)
- **Never** skip `obj.data is not None` check before data property access (Empty objects)
- **Never** mutate original images — copy first, clean up in `finally`
- **Never** use dict positional arg for context overrides — use `temp_override()` (Blender 4.2+)
- **Never** set `hide_render` when toggling visibility — only `hide_viewport`
- **Never** use `as any` / `@ts-ignore` / empty catch blocks (project-wide rule)
- **Never** import `blender_mcp_addon` from `blender_mcp` (separate processes)

## CONVENTIONS (DEVIATIONS ONLY)

- Ruff: line-length 120, select E/F/W/I only (no N/flake8-bugbear)
- `from __future__ import annotations` in every file
- Per-file ignores in `pyproject.toml` (E402 for mcp_protocol, E741 for core_handlers/nodes/reader)
- Response format: `_ok(result=..., started=t)` / `_error(code=..., message=..., started=t)` — never raw dicts
- Tool descriptions use WHAT/WHEN/NOT three-part pattern
- All addon writes go through `_push_undo_step()` for Ctrl+Z
- Fractional FPS: `fps_base=1000` (handles 23.976)
- unittest runner, NOT pytest (conftest.py for path setup only)

## COMMANDS

```bash
uv sync                                                          # Install
uv run python -m unittest discover -s tests -p "test_*.py"      # Tests
uv run ruff check src/ tests/                                    # Lint
uv run python -m examples.stdio_loop                             # Example
ageless-blender-mcp                                              # CLI entry point
```

CI (`.github/workflows/ci.yml`): lint + schema + unit (3.11/3.12/3.13) — 5 jobs total.
