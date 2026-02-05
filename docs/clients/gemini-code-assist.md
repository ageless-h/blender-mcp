# Gemini Code Assist Configuration

## Config File Location

- **Windows**: `%APPDATA%\Code\User\settings.json` (VS Code extension)
- **macOS**: `~/Library/Application Support/Code/User/settings.json`
- **Linux**: `~/.config/Code/User/settings.json`

For JetBrains IDEs, check the plugin settings panel.

## Configuration

For VS Code, add to `settings.json`:

```json
{
  "gemini.codeAssist.mcp.servers": {
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

1. Open VS Code with Gemini Code Assist extension
2. Open Gemini Code Assist panel
3. Check MCP server status
4. Verify "blender" appears as connected

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

### Extension not recognizing MCP
- Reload VS Code window after configuration changes
- Check Gemini Code Assist output panel for errors
