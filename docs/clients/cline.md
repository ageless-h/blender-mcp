# Cline Configuration

## Configuration Method

Cline (VS Code extension) manages MCP servers through its built-in settings UI, not via a manually edited configuration file.

## Configuration Steps

1. Open VS Code with Cline extension installed
2. Open the Cline panel
3. Click on the settings/gear icon
4. Navigate to **MCP Servers** section
5. Click **Add Server** or **Edit MCP Settings**
6. Add the following configuration:

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

## Config File Location (Reference)

Cline stores its configuration in VS Code's globalStorage:

- **Windows**: `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
- **macOS**: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Linux**: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

> **Note**: It's recommended to use the Cline UI to manage MCP servers rather than editing this file directly.

## Verification

1. Open Cline in VS Code
2. Open the Cline panel
3. Check the MCP servers section
4. Verify "blender" appears as connected
5. Ask Cline to list available Blender tools

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
- Restart VS Code after configuration changes
- Check Cline's output panel for error messages
