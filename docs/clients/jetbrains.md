# JetBrains AI Assistant Configuration

## Configuration Method

JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, etc.) configure MCP servers through the built-in settings UI, not via a configuration file.

## Configuration Steps

1. Open your JetBrains IDE
2. Go to **Settings** (or **Preferences** on macOS)
3. Navigate to **Tools > AI Assistant > Model Context Protocol (MCP)**
4. Click **Add** to add a new MCP server
5. Add the following JSON configuration:

```json
{
  "command": "uvx",
  "args": ["blender-mcp"],
  "env": {
    "MCP_ADAPTER": "socket",
    "MCP_SOCKET_HOST": "127.0.0.1",
    "MCP_SOCKET_PORT": "9876"
  }
}
```

> **Prerequisite**: Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first. The `uvx` command will automatically download and run `blender-mcp` from PyPI.

## Alternative: Command Palette

You can also access MCP settings by:
1. Opening AI Assistant chat
2. Typing `/` and selecting **Add Command**
3. Following the prompts to add an MCP server

## Verification

1. Open your JetBrains IDE
2. Open AI Assistant panel (View > Tool Windows > AI Assistant)
3. Check MCP server settings in AI Assistant preferences
4. Verify "blender" appears as connected
5. Test by asking the assistant about Blender tools

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

### AI Assistant not finding MCP
- Restart IDE after configuration changes
- Check Event Log for errors (View > Tool Windows > Event Log)
