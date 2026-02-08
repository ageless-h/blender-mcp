# Source Root

## Packages

### `blender_mcp/`
Core MCP server code including:
- JSON-RPC 2.0 handling
- Security layer (allowlist, permissions, rate limiting)
- Capability catalog
- Adapter interfaces for Blender communication

### `blender_mcp_addon/`
Blender addon package for installation via Blender's addon preferences:
- `__init__.py` - bl_info, register/unregister
- `preferences.py` - Addon preferences (host, port, auto-start)
- `operators.py` - Start/stop server operators
- `server/` - Socket server for MCP communication
- `capabilities/` - Capability dispatcher for blender.* tools
- `handlers/` - Data CRUD, animation, nodes, sequencer, and other handlers
