## Why

The MCP server infrastructure is mature (JSON-RPC 2.0, security layer, capability catalog, adapter interface) but the Blender addon remains a loose collection of PoC scripts in `addon/`. It cannot be installed as a proper Blender addon - missing `bl_info`, `register()`/`unregister()` functions, and proper package structure. For MVP deployment, users need to install the addon through Blender's standard addon preferences UI.

## What Changes

- Create a proper Blender addon package at `src/blender_mcp_addon/` following Blender conventions
- Implement `bl_info` dictionary with addon metadata (name, version, Blender compatibility)
- Add `register()` and `unregister()` functions as Blender entrypoints
- Integrate existing socket server as an operator that starts/stops with the addon
- Create preferences panel for host/port configuration
- Migrate and refactor `execute_capability()` logic into the new package structure
- Keep `addon/` as legacy/PoC reference until migration is verified

## Capabilities

### New Capabilities

- `addon-package-structure`: Defines the Blender addon package layout, bl_info, and registration lifecycle
- `addon-preferences-panel`: User-configurable settings (socket port, auto-start behavior) via Blender preferences
- `addon-socket-operator`: Blender operator to start/stop the MCP socket server with UI feedback

### Modified Capabilities

- `blender-adapter-interface`: Update socket server integration to use the new addon package paths

## Impact

- **Code**: New `src/blender_mcp_addon/` package; `addon/` preserved as reference
- **APIs**: No external API changes; internal restructuring only
- **Dependencies**: No new dependencies (uses Blender's bpy)
- **Testing**: Need Blender environment for addon registration tests
- **Examples**: Update documentation for addon installation instructions
