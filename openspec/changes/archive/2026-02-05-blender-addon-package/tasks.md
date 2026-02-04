## 1. Package Scaffolding

- [x] 1.1 Create `src/blender_mcp_addon/` directory structure
- [x] 1.2 Create `__init__.py` with bl_info dictionary (name, version, blender 3.6+, category)
- [x] 1.3 Create empty `register()` and `unregister()` functions
- [x] 1.4 Create `server/__init__.py` module placeholder
- [x] 1.5 Create `capabilities/__init__.py` module placeholder

## 2. Preferences Panel

- [x] 2.1 Create `preferences.py` with `BlenderMCPPreferences(AddonPreferences)` class
- [x] 2.2 Add `host` StringProperty with default "127.0.0.1"
- [x] 2.3 Add `port` IntProperty with default 9876, min 1024, max 65535
- [x] 2.4 Add `auto_start` BoolProperty with default False
- [x] 2.5 Implement `draw()` method showing host, port, auto_start, and server status
- [x] 2.6 Register preferences class in `register()`, unregister in `unregister()`

## 3. Socket Server Migration

- [x] 3.1 Create `server/socket_server.py` migrating code from `addon/socket_server.py`
- [x] 3.2 Add `is_server_running()` function for status checks
- [x] 3.3 Update imports to use new package paths
- [x] 3.4 Add `get_server_address()` helper to read from preferences

## 4. Capability Handlers Migration

- [x] 4.1 Create `capabilities/base.py` with `execute_capability()` dispatcher
- [x] 4.2 Create `capabilities/scene.py` with `_scene_read()` and `_scene_write()` handlers
- [x] 4.3 Migrate helper functions `_ok()` and `_error()` to base.py
- [x] 4.4 Update socket server to import from `capabilities.base`

## 5. Operators

- [x] 5.1 Create `operators.py` with `MCP_OT_start_server` operator class
- [x] 5.2 Implement start operator `execute()`: read prefs, start server, report status
- [x] 5.3 Create `MCP_OT_stop_server` operator class
- [x] 5.4 Implement stop operator `execute()`: stop server, report status
- [x] 5.5 Register operators in `register()`, unregister in `unregister()`
- [x] 5.6 Add operator buttons to preferences panel draw()

## 6. Registration and Lifecycle

- [x] 6.1 Wire up full `register()`: preferences → operators → auto-start check
- [x] 6.2 Wire up full `unregister()`: stop server → operators → preferences
- [x] 6.3 Add logging for registration events

## 7. Testing and Verification

- [x] 7.1 Test addon installation in Blender via preferences
- [x] 7.2 Test preferences persistence across Blender restart
- [x] 7.3 Test start/stop operators from preferences panel
- [x] 7.4 Test auto-start functionality
- [x] 7.5 Test end-to-end: MCP server → SocketAdapter → addon socket server → scene.read

## 8. Documentation

- [x] 8.1 Update `src/README.md` to document blender_mcp_addon package
- [x] 8.2 Add installation instructions to project README
- [x] 8.3 Document preferences and operator usage
