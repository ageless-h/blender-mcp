# Kiro Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.kiro\settings\mcp.json`
- **macOS**: `~/.kiro/settings/mcp.json`
- **Linux**: `~/.kiro/settings/mcp.json`

For workspace-specific configuration, create `.kiro/settings/mcp.json` in your project root.

> **Note**: Workspace settings take precedence over user settings when both exist.

## Configuration

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": {
        "MCP_ADAPTER": "socket",
        "MCP_SOCKET_HOST": "127.0.0.1",
        "MCP_SOCKET_PORT": "9876"
      }
    }
  }
}
```

> **Prerequisite**: Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first. The `uvx` command will automatically download and run `blender-mcp` from PyPI.

## Alternative: Command Palette

1. Open Command Palette (Cmd+Shift+P on Mac, Ctrl+Shift+P on Windows/Linux)
2. Search for "Kiro: Open user MCP config (JSON)" or "Kiro: Open workspace MCP config (JSON)"
3. Edit the configuration file

## Verification

1. Open Kiro
2. Navigate to MCP server settings
3. Verify "blender" appears in the server list
4. Test by requesting available tools

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
