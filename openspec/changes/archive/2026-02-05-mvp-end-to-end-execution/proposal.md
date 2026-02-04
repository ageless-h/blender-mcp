## Why

The MCP server infrastructure is complete (JSON-RPC 2.0, security layer, capability catalog) and the Blender addon has `execute_capability()` stubs, but they are not connected. Capability requests return `{"status": "accepted"}` without executing anything in Blender. MVP requires end-to-end execution where a client request actually triggers Blender operations and returns real data.

## What Changes

- Add a Blender adapter that bridges the MCP server to the Blender addon process
- Implement capability execution routing so registered capabilities invoke the addon's `execute_capability()`
- Establish a communication channel (socket-based) since the MCP server and Blender run as separate processes
- Wire `scene.read` and `scene.write` to return actual Blender scene data through the full pipeline
- Update `MCPServer.handle_request()` to dispatch to the adapter instead of returning stub responses

## Capabilities

### New Capabilities

- `blender-adapter-interface`: Defines the contract and communication protocol between MCP server and Blender addon process
- `capability-execution-dispatch`: Routes capability requests through the adapter to execute in Blender and return real results

### Modified Capabilities

- `stdio-transport`: Extend to support the adapter initialization flow (addon must be running before transport accepts requests)

## Impact

- **Code**: `src/blender_mcp/adapters/`, `src/blender_mcp/core/server.py`, `addon/entrypoint.py`
- **APIs**: New adapter interface methods; server dispatch logic changes
- **Dependencies**: No new external dependencies (socket stdlib)
- **Testing**: Integration tests require Blender process or mock adapter
- **Examples**: `stdio_loop.py` needs adapter configuration
