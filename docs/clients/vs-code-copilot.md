# VS Code Copilot Configuration

## Config File Location

- **Windows**: `%APPDATA%\Code\User\settings.json`
- **macOS**: `~/Library/Application Support/Code/User/settings.json`
- **Linux**: `~/.config/Code/User/settings.json`

Or create `.vscode/mcp.json` in your workspace root for project-specific configuration.

## Configuration

Create `.vscode/mcp.json` in your workspace root (recommended), or add to your VS Code `settings.json`:

### `.vscode/mcp.json` (Recommended)

```json
{
  "servers": {
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

1. Open VS Code
2. Open the Copilot Chat panel
3. Type `@blender` to see if the MCP server is available
4. Ask Copilot to list available Blender tools

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

### MCP server not recognized
- Ensure you have GitHub Copilot Chat extension installed
- Reload VS Code window after configuration changes
- Check Output panel > "GitHub Copilot Chat" for errors
