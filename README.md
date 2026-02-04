# Blender MCP

MCP server integration for AI-assisted Blender automation.

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

## MCP Server (Stdio Loop)

1. Install the package:
   - `uv sync` or `pip install .`

2. Run the stdio example with socket adapter:
   - `MCP_ADAPTER=socket python -m examples.stdio_loop`

3. Send a JSON-RPC 2.0 line on stdin:
   - `{ "jsonrpc": "2.0", "id": 1, "method": "scene.read", "params": {"payload": {}, "scopes": ["scene:read"]} }`

4. Observe a JSON response on stdout with actual Blender scene data.

## Testing Without Blender

Use the mock adapter for testing without Blender:
```bash
MCP_ADAPTER=mock python -m examples.stdio_loop
```

Notes: Messages are JSON-RPC 2.0 objects serialized as one JSON document per line.
