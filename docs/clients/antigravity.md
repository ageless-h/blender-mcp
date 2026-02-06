# Antigravity Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.gemini\antigravity\mcp_config.json`
- **macOS**: `~/.gemini/antigravity/mcp_config.json`
- **Linux**: `~/.gemini/antigravity/mcp_config.json`

> **Note**: You can also access this file via Antigravity UI: Agent Panel → "..." menu → "Manage MCP Servers" → "View raw config"

## Configuration

```json
{
  "mcpServers": {
    "blender": {
      "command": "<absolute-path-to-python>",
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

**Windows Example:**
```json
{
  "mcpServers": {
    "blender": {
      "command": "C:\\Python313\\python.exe",
      "args": ["-m", "blender_mcp.mcp_protocol"],
      "env": {
        "MCP_ADAPTER": "socket",
        "MCP_SOCKET_HOST": "127.0.0.1",
        "MCP_SOCKET_PORT": "9876",
        "PYTHONPATH": "C:\\path\\to\\blender-mcp\\src"
      }
    }
  }
}
```

> **Important**: Use absolute paths for both `command` and `PYTHONPATH`. On Windows, use escaped backslashes (`\\`).

## Verification

1. **Restart Antigravity** after modifying the config file
2. Open the MCP server management panel
3. Verify "blender" appears in the server list with no errors
4. The available tools should include: `data_create`, `data_read`, `data_write`, etc.

## Troubleshooting

### Server not recognized after config change
- **Restart Antigravity** - config changes require a restart to take effect

### Python not found
- Use **absolute path** to Python executable (e.g., `C:\\Python313\\python.exe`)
- Verify Python is installed and the path is correct

### PYTHONPATH issues
- Use **absolute path** for PYTHONPATH
- On Windows, use escaped backslashes (`\\`) not forward slashes

### Tool name errors (regex violation)
- Ensure you're using the latest version of blender-mcp
- Tool names should be `data_create`, `data_read`, etc. (underscores, not dots)

### Connection refused
- Ensure Blender is running with the MCP addon enabled
- Verify the addon server is started (check "Start Server" button in addon panel)
- Confirm host/port match addon settings (default: `127.0.0.1:9876`)
- Check firewall settings
