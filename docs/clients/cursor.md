# Cursor Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.cursor\mcp.json`
- **macOS**: `~/.cursor/mcp.json`
- **Linux**: `~/.cursor/mcp.json`

Alternatively, create `.cursor/mcp.json` in your project root for project-specific configuration.

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

## Verification

1. Open Cursor
2. Open the Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
3. Search for "MCP: List Servers"
4. Verify "blender" appears in the server list
5. Check the MCP panel for available tools

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

### Server not appearing
- Restart Cursor after configuration changes
- Check Cursor's developer console for errors (Help > Toggle Developer Tools)
