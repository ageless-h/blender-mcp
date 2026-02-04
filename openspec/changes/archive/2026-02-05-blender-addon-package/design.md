# Design: Blender Addon Package

## Overview

Transform the PoC addon code into a proper Blender addon package that can be installed through Blender's standard addon preferences UI.

## Package Structure

```
src/blender_mcp_addon/
├── __init__.py          # bl_info, register(), unregister()
├── preferences.py       # AddonPreferences class
├── operators.py         # MCP_OT_start_server, MCP_OT_stop_server
├── server/
│   ├── __init__.py
│   └── socket_server.py # Socket server (migrated from addon/)
└── capabilities/
    ├── __init__.py
    ├── base.py          # execute_capability dispatcher
    └── scene.py         # scene.read, scene.write handlers
```

## Key Decisions

### Decision: Package location at `src/blender_mcp_addon/`
**Rationale**: Keeps addon code in `src/` alongside `blender_mcp/` (MCP server code). Clear separation: server code vs addon code. Enables shared tooling (linting, testing setup).

**Alternative considered**: Keep in `addon/` directory.
**Rejected because**: `addon/` contains PoC code; cleaner to start fresh with proper structure.

### Decision: bl_info with Blender 3.6+ support
**Rationale**: Blender 3.6 is LTS (Long Term Support), 4.x is current. Supporting both covers majority of users.

```python
bl_info = {
    "name": "Blender MCP",
    "author": "Blender MCP Contributors",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "category": "Development",
    "description": "MCP server integration for AI-assisted Blender automation",
}
```

### Decision: Preferences-driven configuration
**Rationale**: Users expect addon settings in Blender's preferences. Persists across sessions. Standard Blender UX pattern.

Properties:
- `host`: StringProperty, default "127.0.0.1"
- `port`: IntProperty, default 9876, min 1024, max 65535
- `auto_start`: BoolProperty, default False

### Decision: Operators for server control
**Rationale**: Blender operators provide undo support, logging, and UI integration. Can be called from menus, buttons, or scripts.

- `mcp.start_server` - Start socket server
- `mcp.stop_server` - Stop socket server

### Decision: Thread-based socket server
**Rationale**: Socket server must not block Blender's main thread. Python threading is sufficient for I/O-bound socket operations. Matches existing `addon/socket_server.py` approach.

### Decision: Preserve execute_capability contract
**Rationale**: SocketAdapter in `blender_mcp` already expects specific request/response format. Changing would require coordinated updates. Contract is well-defined and working.

## Registration Flow

```
register():
    1. Register preferences class
    2. Register operators
    3. If auto_start enabled:
       - Start socket server with configured host:port

unregister():
    1. Stop socket server if running
    2. Unregister operators
    3. Unregister preferences class
```

## Migration Strategy

1. Create new package structure
2. Migrate socket server code from `addon/socket_server.py`
3. Migrate capability handlers from `addon/entrypoint.py`
4. Add Blender addon boilerplate (bl_info, register, preferences)
5. Test installation in Blender
6. Keep `addon/` as reference until verified

## Testing Approach

- Unit tests for capability handlers (mock bpy)
- Manual testing in Blender for:
  - Addon installation/removal
  - Preferences persistence
  - Server start/stop operators
  - End-to-end capability execution
