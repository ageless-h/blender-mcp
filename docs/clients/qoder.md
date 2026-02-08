# Qoder Configuration

## Configuration Method

Qoder manages MCP servers through its built-in settings UI.

## Configuration Steps

### In Qoder IDE

1. Open Qoder IDE
2. Click on the user icon or use keyboard shortcut:
   - **macOS**: `⌘ ⇧ ,`
   - **Windows/Linux**: `Ctrl Shift ,`
3. Select **Qoder Settings**
4. Navigate to **MCP** in the left navigation
5. Click **Add Server** and configure:

```json
{
  "blender": {
    "transport": "stdio",
    "command": "uvx",
    "args": ["ageless-blender-mcp"],
    "env": {
      "MCP_ADAPTER": "socket",
      "MCP_SOCKET_HOST": "127.0.0.1",
      "MCP_SOCKET_PORT": "9876"
    }
  }
}
```

> **Prerequisite**: Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first. The `uvx` command will automatically download and run `ageless-blender-mcp` from PyPI.

### In Qoder AI Chat Panel

1. Open the Qoder AI Chat panel
2. Click the dropdown menu in the top-right corner
3. Select **Your Settings**
4. Navigate to **MCP Servers**

## Config File Location (Reference)

Qoder may store configurations in:
- **User Level**: `~/.qoder/settings.json`
- **Project Level**: `${project}/.qoder/settings.json`
- **Windows**: `%USERPROFILE%\.Qoder\`

> **Note**: It's recommended to use the Qoder UI to manage MCP servers.

## Verification

1. Open Qoder
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
