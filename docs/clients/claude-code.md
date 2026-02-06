# Claude Code CLI Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.claude\mcp.json`
- **macOS**: `~/.claude/mcp.json`
- **Linux**: `~/.claude/mcp.json`

For project-specific configuration, create `.claude/mcp.json` in your project root.

> **Note**: For Claude Desktop app, see [Claude Desktop documentation](https://docs.anthropic.com/en/docs/agents-and-tools/mcp).

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
