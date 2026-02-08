# OpenCode Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.config\opencode\opencode.jsonc`
- **macOS**: `~/.config/opencode/opencode.json`
- **Linux**: `~/.config/opencode/opencode.json`

For project-specific configuration, create `.opencode/opencode.json` in your project root.

## Configuration

Add to your `opencode.json`:

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

1. Run OpenCode
2. Check MCP server status
3. Verify "blender" appears as connected
4. Test by requesting Blender tools

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
