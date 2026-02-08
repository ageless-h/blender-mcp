# Codex CLI Configuration

## Config File Location

- **Windows**: `%USERPROFILE%\.codex\config.toml`
- **macOS**: `~/.codex/config.toml`
- **Linux**: `~/.codex/config.toml`

For project-specific configuration, create `.codex/config.toml` in your project root (requires trusted project).

## Configuration

Add to your `config.toml`:

```toml
[mcp_servers.blender]
type = "stdio"
launcher_command = "uvx ageless-blender-mcp"

[mcp_servers.blender.env_vars]
MCP_ADAPTER = "socket"
MCP_SOCKET_HOST = "127.0.0.1"
MCP_SOCKET_PORT = "9876"
```

> **Prerequisite**: Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first. The `uvx` command will automatically download and run `ageless-blender-mcp` from PyPI.

## Verification

1. Run Codex CLI
2. Use `/mcp` command to verify servers
3. Check that "blender" appears as available
4. Test by calling a Blender tool

## Troubleshooting

### Python not found
- Ensure Python is in your system PATH
- Use absolute path to Python executable in the `launcher_command` field

### PYTHONPATH issues
- Use absolute path for PYTHONPATH
- On Windows, use forward slashes or escaped backslashes

### Connection refused
- Ensure Blender addon is running and server is started
- Verify host and port match addon settings
- Check firewall settings
