# Gemini Code Assist Configuration

## Config File Location

MCP servers for Gemini Code Assist are configured in `.gemini/settings.json`:

- **Global**: `~/.gemini/settings.json` (macOS/Linux) or `%USERPROFILE%\.gemini\settings.json` (Windows)
- **Project**: `.gemini/settings.json` in your project root

## Configuration

Add to your `.gemini/settings.json`:

```json
{
  "mcpServers": {
    "blender": {
      "type": "stdio",
      "command": "uvx",
      "args": ["ageless-blender-mcp"],
      "env": {
        "MCP_ADAPTER": "socket",
        "MCP_SOCKET_HOST": "127.0.0.1",
        "MCP_SOCKET_PORT": "9876"
      }
    }
  }
}
```

> **Prerequisite**: Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first. The `uvx` command will automatically download and run `ageless-blender-mcp` from PyPI.

## VS Code Extension Settings

For additional Gemini Code Assist extension settings in VS Code:
1. Open VS Code Settings (Ctrl/Cmd + ,)
2. Search for "Gemini Code Assist"
3. Configure extension preferences as needed

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
