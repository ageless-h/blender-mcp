# Warp Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.warp\mcp.json`
- **macOS**: `~/.warp/mcp.json`
- **Linux**: `~/.warp/mcp.json`

## Configuration

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

Replace `<path-to-blender-mcp>` with the actual path to your Blender MCP installation.

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
- Check Warp's settings panel for error messages
