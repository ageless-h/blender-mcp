# Protocol and Transport Choices

> 更新日期: 2026-02-08

## Protocol
- JSON-RPC 2.0 over MCP (Model Context Protocol)。
- MCPServer (`src/blender_mcp/mcp_protocol.py`) 处理 `initialize`、`tools/list`、`tools/call`、`prompts/list`、`prompts/get` 等 JSON-RPC 方法。
- 26 个工具通过 `tools/list` 暴露，每个工具带有 `inputSchema` (JSON Schema) 和 MCP 注解。
- 旧工具名称通过 `_LEGACY_TOOL_MAP` 自动映射到新的 `blender_*` 工具。

## Transport
- **stdio**: `examples/stdio_loop.py` 提供 JSON-line 循环，用于开发和调试。
- **Socket**: `src/blender_mcp_addon/server/` 提供 TCP socket 服务器，运行在 Blender addon 内部，MCP 服务端通过 `SocketAdapter` 与之通信。
- 未来扩展: WebSocket 传输层可通过 `src/blender_mcp/transport/` 接口添加。

## 数据流

```
MCP Client (Claude/IDE)
  ↓ JSON-RPC 2.0
MCPServer (mcp_protocol.py)
  ↓ tools_call → adapter.execute(capability, payload)
SocketAdapter / MockAdapter
  ↓ TCP socket (或 mock)
Blender Addon (blender_mcp_addon)
  ↓ execute_capability(request)
Handler 层 (capabilities/base.py → handlers/*)
  ↓ bpy.*
Blender
```

## Dependency Policy
- Pin MCP SDK versions to avoid breaking changes.
- Prefer official SDKs and minimize third-party protocol layers.
