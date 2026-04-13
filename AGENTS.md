# AGENTS

## Project Overview

Blender MCP — MCP server integration for AI-assisted Blender automation.
- **Package**: `ageless-blender-mcp` on PyPI
- **Version**: 1.2.0
- **Python**: >=3.11
- **Blender**: 4.2 LTS / 4.5 LTS / 5.0+ / 5.1

## Project Structure

```
src/
  blender_mcp/          # MCP server package (published to PyPI)
    adapters/            # Socket/Mock adapter layer
    catalog/             # Tool capability catalog
    schemas/             # JSON Schema definitions
    security/            # Allowlist, audit, guardrails
    prompts/             # MCP prompt templates
    versioning/          # Blender version compatibility
    mcp_protocol.py      # MCP protocol entry point
  blender_mcp_addon/    # Blender addon (runs inside Blender)
    capabilities/        # Capability dispatcher + base handler
    handlers/            # Tool handlers (nodes, sequencer, etc.)
    operators.py         # Blender operators (start/stop server, show panel, clear log)
    preferences.py       # Addon preferences (host, port, auto-start, hotkey)
    ui.py                # Global statusbar + popup panel, i18n support
    server/              # Socket server for addon-MCP communication
      op_log.py          # Thread-safe operation log with stats
      timeouts.py        # Per-capability dynamic timeout tiers
tests/
  addon/                # Addon unit tests (mocked Blender)
  integration/          # Integration tests
  mcp/                  # MCP protocol tests
  tools/                # Tool schema validation
docs/
  capabilities/         # Tool catalog, status, roadmap
  testing/              # Test plans + advanced test suite
  clients/              # MCP client integration guides
docs/testing/advanced-test-suite.md  # 10 advanced real-Blender test scenarios
```

## Execution Guidance

- Keep changes minimal and aligned to OpenSpec artifacts.
- Prefer updating tests and examples alongside behavior changes.
- All write operations in the addon go through `_push_undo_step()` for Ctrl+Z support.
- Node name lookup in `edit_nodes` uses 3-tier fallback: exact name → bl_idname → English display-name mapping + dynamic `_discover_node_types()`.
- UI is global: statusbar indicator (all editors) + popup panel (Ctrl+Shift+M or click statusbar).

## Verification Steps

- Run unit and integration tests: `uv run python -m unittest discover -s tests -p "test_*.py"`
- Run the stdio example: `python -m examples.stdio_loop`

## Common Commands

- Install: `uv sync`
- Run example: `python -m examples.stdio_loop`
- Run tests: `uv run python -m unittest discover -s tests -p "test_*.py"`
- Lint: `uv run ruff check src/ tests/`
