# Claude Code CLI Configuration

## Config File Location

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/.claude/mcp.json`
- **Linux**: `~/.claude/mcp.json`

For project-specific configuration, create `.claude/mcp.json` in your project root.

> **Note**: For Claude Desktop app, see [Claude Desktop documentation](https://docs.anthropic.com/en/docs/agents-and-tools/mcp).

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

1. Run Claude Code CLI with `claude`
2. Use `/mcp` command to list servers
3. Verify "blender" appears in the connected servers list
4. Start a conversation and ask Claude to list available Blender tools

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
- Restart Claude Code CLI after configuration changes
- Check that the MCP server process is running
