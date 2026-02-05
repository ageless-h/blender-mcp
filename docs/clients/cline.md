# Cline Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.cline\mcp_settings.json`
- **macOS**: `~/.cline/mcp_settings.json`
- **Linux**: `~/.cline/mcp_settings.json`

Or configure via VS Code settings if using Cline as an extension.

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

1. Open Cline in VS Code
2. Open the Cline panel
3. Check the MCP servers section
4. Verify "blender" appears as connected
5. Ask Cline to list available Blender tools

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
- Restart VS Code after configuration changes
- Check Cline's output panel for error messages
