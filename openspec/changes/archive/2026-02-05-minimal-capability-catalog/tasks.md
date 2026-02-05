## 1. Align capability definitions (catalog + docs)

- [x] 1.1 Update `blender_mcp.catalog.catalog.minimal_capability_set()` to include the 7 minimal capabilities defined in this change (names, descriptions, scopes, min_version/max_version)
- [x] 1.2 Ensure scopes are defined for all capabilities that require authorization (e.g. `scene:read`, `object:read`, `object:write`, `render:read`, `render:execute`) and are consistent with `PermissionPolicy` usage
- [x] 1.3 Update `docs/capabilities/catalog.md` minimum capability set list and field names to match implementation (`scopes`, `min_version`, `max_version`)

## 2. Wire catalog into runtime (discovery + policy)

- [x] 2.1 Add `CapabilityCatalog` as a dependency on `MCPServer` (inject at construction) so runtime can expose catalog-backed functionality
- [x] 2.2 Implement a discovery capability (e.g. `capabilities.list`) that returns the canonical catalog entries (name/description/scopes/min_version/max_version and availability metadata if implemented)
- [x] 2.3 Ensure discovery capability is protected by allowlist/permissions/rate limiting like any other capability
- [x] 2.4 Update `examples/stdio_loop.py` to register the expanded minimal capability set and configure allowlist/permissions/rate limits consistently

## 3. Validation and tests

- [x] 3.1 Add/extend unit tests to assert the minimal capability set contains all required entries and required scope mappings are enforced
- [x] 3.2 Add/extend tests for capability discovery returning the canonical catalog (and that it stays in sync with `minimal_capability_set()`)
- [x] 3.3 Add/extend tests for version constraint handling (capabilities outside `min_version/max_version` are marked unavailable with a reason, if implemented)

## 4. Verification

- [x] 4.1 Run unit and integration tests: `uv run python -m unittest discover -s tests -p "test_*.py"`
- [x] 4.2 Run the stdio example: `python -m examples.stdio_loop`
