# Amp Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.config\amp\settings.json`
- **macOS**: `~/.config/amp/settings.json`
- **Linux**: `~/.config/amp/settings.json`

For workspace-specific configuration, create `.amp/settings.json` in your project root.

## Configuration

Add to your `settings.json`:

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

1. Open Amp
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
