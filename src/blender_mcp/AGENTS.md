# blender_mcp — MCP Server Package

Published to PyPI as `ageless-blender-mcp`. Standalone MCP server (stdio/SSE) that translates tool calls into TCP commands to the Blender addon.

## STRUCTURE

```
mcp_protocol.py       # MCPServer — entry point, run_mcp_server(), 29 tools
schemas/tools.py      # TOOL_DEFINITIONS list, _tool() helper, _vec3() fragments
adapters/
  base.py             # Adapter ABC
  socket.py           # SocketAdapter — TCP to Blender addon
  mock.py             # MockAdapter — testing without Blender (MCP_ADAPTER=mock)
  plugin_contract.py  # Adapter plugin interface
  types.py            # Shared adapter types
security/
  allowlist.py        # Tool/capability allowlist
  guardrails.py       # Input validation
  rate_limit.py       # Per-client rate limiting
  audit.py            # JsonFileAuditLogger + MemoryAuditLogger
prompts/registry.py   # Empty prompt registry (prompts removed)
telemetry.py          # Opt-in telemetry tool
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Add a new tool | `schemas/tools.py` | `_tool()` helper → `TOOL_DEFINITIONS` list |
| Change adapter behavior | `adapters/socket.py` or `mock.py` | Both implement `Adapter` ABC from `base.py` |
| Add security rule | `security/guardrails.py` | Pipeline: Allowlist → Guardrails → RateLimiter → Audit |
| Debug tool dispatch | `mcp_protocol.py` | `_handle_tool_call()` method |

## CONVENTIONS

- Tool descriptions: **WHAT/WHEN/NOT** three-part pattern (mandatory)
- Tool schema: hand-written JSON Schema in `_tool()` helper, shared fragments (`_vec3()`, `_color()`)
- Adapter selection: `MCP_ADAPTER` env var → `MockAdapter` if `"mock"`, else `SocketAdapter`
- CLI entry points: `ageless-blender-mcp` and `blender-mcp` both map to `run_mcp_server()`
- Zero runtime dependencies — stdlib only
- Absolute imports: `from blender_mcp.adapters...` (never relative)
- **Never** import from `blender_mcp_addon` (separate process)

## ADDING A NEW TOOL (4 STEPS)

1. `schemas/tools.py` — define with `_tool()` helper, add to `TOOL_DEFINITIONS`
2. `blender_mcp_addon/handlers/` — implement handler (separate package)
3. `tests/tools/` — add schema validation test
4. Run: `uv run python -m unittest discover -s tests/tools -p "test_*.py"`
