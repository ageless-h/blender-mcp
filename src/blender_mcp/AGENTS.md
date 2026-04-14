# blender_mcp — MCP Server Package

Published to PyPI as `ageless-blender-mcp`. Standalone MCP server (stdio/SSE) that translates tool calls into TCP commands to the Blender addon. **154 Python files, 22,606 lines project-wide.**

## STRUCTURE

```
mcp_protocol.py       # MCPServer — entry point, run_mcp_server(), 26 tools, 10 prompts
schemas/tools.py      # 1480 lines — TOOL_DEFINITIONS list, _tool() helper, _vec3() fragments
adapters/
  base.py             # Adapter ABC
  socket.py           # SocketAdapter — TCP to Blender addon
  mock.py             # MockAdapter — testing without Blender (MCP_ADAPTER=mock)
  plugin_contract.py  # Adapter plugin interface
  types.py            # Shared adapter types
catalog/catalog.py    # CapabilityCatalog + CapabilityMeta (version-scoped)
security/
  allowlist.py        # Tool/capability allowlist
  guardrails.py       # Input validation
  rate_limit.py       # Per-client rate limiting
  audit.py            # JsonFileAuditLogger + MemoryAuditLogger
prompts/registry.py   # 10 prompts (7 workflow + 3 strategy) with argument schemas
versioning/           # Blender version compat (4.2/4.5/5.0/5.1)
telemetry.py          # Opt-in telemetry tool
```

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Add a new tool | `schemas/tools.py` | `_tool()` helper → `TOOL_DEFINITIONS` list |
| Register capability | `catalog/catalog.py` | `CapabilityMeta(name, scopes, min_version)` |
| Change adapter behavior | `adapters/socket.py` or `mock.py` | Both implement `Adapter` ABC from `base.py` |
| Add security rule | `security/guardrails.py` | Pipeline: Allowlist → Guardrails → RateLimiter → Audit |
| Add MCP prompt | `prompts/registry.py` | Dict entry with `name`, `title`, `description`, `arguments` |
| Debug tool dispatch | `mcp_protocol.py` | `_handle_tool_call()` method |

## CONVENTIONS

- Tool descriptions: **WHAT/WHEN/NOT** three-part pattern (mandatory)
- Tool schema: hand-written JSON Schema in `_tool()` helper, shared fragments (`_vec3()`, `_color()`)
- Adapter selection: `MCP_ADAPTER` env var → `MockAdapter` if `"mock"`, else `SocketAdapter`
- CLI entry points: `ageless-blender-mcp` and `blender-mcp` both map to `run_mcp_server()`
- Zero runtime dependencies — stdlib only
- Absolute imports: `from blender_mcp.adapters...` (never relative)
- **Never** import from `blender_mcp_addon` (separate process)

## ADDING A NEW TOOL (5 STEPS)

1. `schemas/tools.py` — define with `_tool()` helper, add to `TOOL_DEFINITIONS`
2. `catalog/catalog.py` — register `CapabilityMeta` with version scope
3. `blender_mcp_addon/handlers/` — implement handler (separate package)
4. `tests/tools/` — add schema validation test
5. Run: `uv run python -m unittest discover -s tests/tools -p "test_*.py"`
