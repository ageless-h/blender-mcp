# GitHub Copilot CLI Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.copilot\mcp-config.json`
- **macOS**: `~/.copilot/mcp-config.json`
- **Linux**: `~/.copilot/mcp-config.json`

For project-specific configuration, create `.copilot/mcp-config.json` in your project root.

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

## Alternative: CLI Command

You can also add MCP servers using the CLI:

```bash
gh copilot mcp add blender
```

## Verification

1. Run `gh copilot` in terminal
2. Use `/mcp` command to check MCP server status
3. Verify "blender" appears as available
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
