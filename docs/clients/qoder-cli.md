# Qoder CLI Configuration

## Configuration Method

Qoder CLI shares configuration with the Qoder IDE, primarily managed through the UI.

## Config File Location (Reference)

- **User Level**: `~/.qoder/settings.json`
- **Project Level**: `${project}/.qoder/settings.json`
- **Windows**: `%USERPROFILE%\.Qoder\`

## Configuration

If editing the settings file directly, add to your `settings.json`:

```json
{
  "mcpServers": {
    "blender": {
      "transport": "stdio",
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

> **Note**: It's recommended to configure MCP servers through the Qoder IDE settings UI instead of editing files directly.

## Verification

1. Run Qoder CLI
2. Check MCP server status
3. Verify "blender" appears as available
4. Test by calling a Blender tool

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
