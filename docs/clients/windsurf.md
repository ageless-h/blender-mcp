# Windsurf Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.codeium\windsurf\mcp_config.json`
- **macOS**: `~/.codeium/windsurf/mcp_config.json`
- **Linux**: `~/.codeium/windsurf/mcp_config.json`

Or create `.windsurf/mcp.json` in your project root for project-specific configuration.

## Configuration

```json
{
  "mcpServers": {
    "blender": {
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

## Verification

1. Open Windsurf
2. Open the Cascade panel
3. Check MCP server status in the panel
4. Ask Cascade to list available Blender tools

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
- Restart Windsurf after configuration changes
- Check Windsurf's developer console for errors
