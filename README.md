# Blender MCP

MCP server integration for AI-assisted Blender automation.

## Unified Tool Architecture

Blender MCP uses a highly compressed tool architecture with **8 core tools** that cover 99.9% of Blender functionality:

| Tool | Description |
|------|-------------|
| `data.create` | Create any Blender data block (objects, meshes, materials, etc.) |
| `data.read` | Read properties from any data block |
| `data.write` | Write properties to any data block |
| `data.delete` | Delete data blocks |
| `data.list` | List all data blocks of a type |
| `data.link` | Link/unlink data blocks (e.g., object to collection) |
| `operator.execute` | Execute any Blender operator (bpy.ops.*) |
| `info.query` | Query status, history, statistics, and viewport capture |

**Optional (disabled by default):**
- `script.execute` - Execute arbitrary Python code (requires explicit enablement)

### Example: Create and Transform an Object

```json
// Create a cube
{"capability": "data.create", "payload": {"type": "object", "name": "MyCube", "params": {"object_type": "MESH"}}}

// Move it
{"capability": "data.write", "payload": {"type": "object", "name": "MyCube", "properties": {"location": [1, 2, 3]}}}

// Add a subdivision modifier
{"capability": "operator.execute", "payload": {"operator": "object.modifier_add", "params": {"type": "SUBSURF"}}}

// Capture the viewport
{"capability": "info.query", "payload": {"type": "viewport_capture", "params": {"format": "base64"}}}
```

See [docs/migration/tools-migration.md](docs/migration/tools-migration.md) for detailed documentation.

## Blender Addon Installation

1. Copy or symlink `src/blender_mcp_addon/` to your Blender addons folder:
   - Windows: `%APPDATA%\Blender\<version>\scripts\addons\blender_mcp_addon`
   - macOS: `~/Library/Application Support/Blender/<version>/scripts/addons/blender_mcp_addon`
   - Linux: `~/.config/blender/<version>/scripts/addons/blender_mcp_addon`

2. In Blender, go to Edit > Preferences > Add-ons

3. Search for "Blender MCP" and enable it

4. Configure the addon in the preferences panel:
   - **Host**: Socket server bind address (default: 127.0.0.1)
   - **Port**: Socket server port (default: 9876)
   - **Auto-start**: Start server automatically when addon is enabled

5. Click "Start Server" to begin accepting MCP requests

### MCP Client Configuration

Create `.mcp.json` in your project root to configure MCP clients:

```json
{
  "mcpServers": {
    "blender": {
      "command": "python",
      "args": ["-m", "blender_mcp.mcp_protocol"],
      "env": {
        "MCP_ADAPTER": "socket",
        "MCP_SOCKET_HOST": "127.0.0.1",
        "MCP_SOCKET_PORT": "9876",
        "PYTHONPATH": "<path-to-blender-mcp>/src"
      }
    }
  }
}
```

## MCP Server (Stdio Loop)

1. Install the package:
   - `uv sync` or `pip install .`

2. Run the stdio example with socket adapter:
   - `MCP_ADAPTER=socket python -m examples.stdio_loop`

3. Send a JSON-RPC 2.0 line on stdin:
   - `{ "jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {} }`
   - `{ "jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "data.read", "arguments": {"payload": {"type": "context"}}} }`

4. Observe a JSON response on stdout with actual Blender scene data.

### Using the MCP Protocol Adapter

The `mcp_protocol.py` module provides a standard MCP protocol layer:

```bash
python -m blender_mcp.mcp_protocol
```

This implements the MCP `2024-11-05` protocol and exposes Blender capabilities as MCP tools:
- `tools/list` - List available tools
- `tools/call` - Execute a Blender operation
- `initialize` - Protocol handshake

## Testing Without Blender

Use the mock adapter for testing without Blender:
```bash
MCP_ADAPTER=mock python -m examples.stdio_loop
```

Notes: Messages are JSON-RPC 2.0 objects serialized as one JSON document per line.
