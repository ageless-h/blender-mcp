# Visual Studio Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.vs\mcp.json`

Visual Studio MCP support is Windows-only.

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

1. Open Visual Studio
2. Go to Tools > Options > GitHub Copilot > MCP Servers
3. Verify "blender" appears in the server list
4. Test in Copilot Chat by asking about Blender tools

## Troubleshooting

### Python not found
- Ensure Python is in your system PATH
- Use absolute path to Python executable in the `command` field

### PYTHONPATH issues
- Use absolute path for PYTHONPATH
- Use forward slashes or escaped backslashes in paths

### Connection refused
- Ensure Blender addon is running and server is started
- Verify host and port match addon settings
- Check Windows Firewall settings

### Server not appearing
- Restart Visual Studio after configuration changes
- Check Output window > GitHub Copilot for errors
