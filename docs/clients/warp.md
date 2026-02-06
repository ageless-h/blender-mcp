# Warp Configuration

## Configuration Method

Warp terminal configures MCP servers through its built-in settings UI.

## Configuration Steps

1. Open Warp terminal
2. Access MCP settings through one of these methods:
   - **Settings Page**: Settings > MCP Servers
   - **Warp Drive**: Personal > MCP Servers
   - **Command Palette**: Search for "Open MCP Servers"
   - **AI Settings**: Settings > AI > Manage MCP servers
3. Click **Add Server** and paste the following configuration:

```json
{
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
```

Replace `<path-to-blender-mcp>` with the actual path to your Blender MCP installation.

## Config File Location (Reference)

Warp may store configurations in:
- **macOS**: `~/.warp/config.json`

> **Note**: It's recommended to use the Warp UI to manage MCP servers rather than editing config files directly.

## Verification

1. Open Warp terminal
2. Open Warp AI panel
3. Check MCP server status in settings
4. Verify "blender" appears as connected
5. Test by asking Warp AI about Blender tools

## Troubleshooting

### Python not found
- Ensure Python is in your system PATH
- Use absolute path to Python executable in the `command` field

### PYTHONPATH issues
- Use absolute path for PYTHONPATH
- On Windows, use forward slashes or escaped backslashes

### Connection refused
- Ensure Blender addon is running and server is started
- Verify host and port match addon settings
- Check firewall settings

### Server not connecting
- Restart Warp after configuration changes
- Check MCP logs at `~/Library/Application Support/dev.warp.Warp/mcp_logs/` (macOS)
