# tests — Test Suite

unittest-based (NOT pytest). 17 addon tests, 7 schema tests, 5 integration tests, 2 MCP tests. All must pass without Blender installed (`MCP_ADAPTER=mock`).

## STRUCTURE

```
conftest.py                     # ROOT, SRC, TESTS paths; MCP_ADAPTER=mock fixture; src/ on sys.path
addon/                          # 17 handler tests (mocked bpy)
  test_animation_editor.py      # Keyframe/NLA/shape-key/driver (635 lines — largest test)
  test_bug_regression.py        # Regression tests for 10 bugs from fix sprint
  test_capabilities_dispatcher.py  # Tool dispatch routing
  test_constraints_handler.py   # Constraint CRUD + move_up/move_down
  test_data_dispatcher.py       # Data type dispatch
  test_generic_handler.py       # GenericCollectionHandler base
  test_handlers.py              # Registration + lifecycle
  test_importexport_handler.py  # Import/export
  test_node_editor.py           # Node tree reader + editor
  test_operator_executor.py     # bpy.ops execution
  test_physics_handler.py       # Physics simulation CRUD
  test_response.py              # Response format helpers
  test_scene_config.py          # Scene setup + render config
  test_script_executor.py       # Script execution
  test_sequencer_editor.py      # VSE operations
  test_shared_utilities.py      # Shared utility functions
  test_uv_handler.py            # UV mapping operations
tools/                          # 7 schema validation tests
  test_schema_validation.py     # All 26 tool schemas valid JSON Schema
  test_declarative_tools.py     # Declarative tool definitions
  test_imperative_tools.py      # Imperative tool definitions
  test_fallback_tools.py        # Fallback tool behavior
  test_param_passing.py         # Parameter transformation
  test_perception_tools.py      # Perception tool schemas
integration/
  real_blender/                 # E2E tests (require live Blender)
    test_all_26_tools.py        # 549 lines — comprehensive tool test
mcp/                           # MCP protocol tests
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Test a handler | `addon/test_<handler>.py` | Mock bpy, check `response["ok"]` |
| Validate tool schemas | `tools/test_schema_validation.py` | JSON Schema validity + annotations |
| Real Blender E2E | `integration/real_blender/` | Requires Blender running |
| MCP protocol tests | `mcp/` | JSON-RPC dispatch |
| Add test fixture | `conftest.py` | Session-scoped, `use_mock_adapter` |

## CONVENTIONS

- **Runner**: `unittest` via `uv run python -m unittest discover` — NOT pytest
- **conftest.py**: Path setup only (`ROOT`, `SRC`, `TESTS`), `use_mock_adapter` fixture
- **bpy mocking**: `MCP_ADAPTER=mock` env var → `MockAdapter` selected
- **Assertions**: Check `response["ok"]` is `True`/`False`, then `response["result"]` or `response["error"]`
- **Root-level tests**: `test_adapters.py`, `test_allowlist.py`, `test_guardrails.py`, etc. — test MCP server logic

## COMMANDS

```bash
uv run python -m unittest discover -s tests -p "test_*.py"        # All tests
uv run python -m unittest tests/addon/test_response.py             # Single file
uv run python -m unittest discover -s tests/tools -p "test_*.py"  # Schema only
```

CI (`.github/workflows/ci.yml`): lint + unit (3.11/3.12/3.13) — 2 jobs.

## ADDING TESTS

- Addon handler → `tests/addon/test_<name>.py` (mock bpy)
- Schema validation → `tests/tools/test_<name>.py`
- Real Blender E2E → `tests/integration/real_blender/` (needs live Blender)
- MCP protocol → `tests/mcp/`
- **All tests must pass without Blender installed** (mock mode)
