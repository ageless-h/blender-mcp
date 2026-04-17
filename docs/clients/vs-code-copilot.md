# VS Code Copilot Configuration

## Config File Location

VS Code stores MCP configuration in `mcp.json`, not `settings.json`. Options:

- **Workspace**: `.vscode/mcp.json` in your project root (recommended)
- **User profile**: Run `MCP: Open User Configuration` from the Command Palette (Ctrl+Shift+P)

## Configuration

Create `.vscode/mcp.json` in your workspace root:

```json
{
  "servers": {
    "blender": {
      "type": "stdio",
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

### MCP server shows but Copilot can't use tools
- **Trust the server**: VS Code prompts you to trust new MCP servers. Check for a trust notification and approve it.
- **Check MCP logs**: Open Output panel, select "MCP" or "GitHub Copilot Chat" from the dropdown.
- **Model availability**: Some Copilot models may not support MCP tools. Try switching models in Copilot Chat (e.g., from a preview model to a stable one).

## Notes

- **Painting/Sculpting/Drawing**: These workflows typically go through `blender_execute_operator` rather than dedicated tools, since they rely on Blender's interactive operators.
- **Root key**: VS Code MCP config uses `"servers"` as the root key, not `"mcpServers"` (which other clients use).
