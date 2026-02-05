# JetBrains AI Assistant & Junie Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.config\JetBrains\<product><version>\mcp.json`
- **macOS**: `~/Library/Application Support/JetBrains/<product><version>/mcp.json`
- **Linux**: `~/.config/JetBrains/<product><version>/mcp.json`

Where `<product>` is your JetBrains IDE (IntelliJIdea, PyCharm, WebStorm, etc.) and `<version>` is the version number.

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

1. Open your JetBrains IDE
2. Open AI Assistant panel (View > Tool Windows > AI Assistant)
3. Check MCP server settings in AI Assistant preferences
4. Verify "blender" appears as connected
5. Test by asking the assistant about Blender tools

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

### AI Assistant not finding MCP
- Restart IDE after configuration changes
- Check Event Log for errors (View > Tool Windows > Event Log)
