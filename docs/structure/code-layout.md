# Code Layout Conventions

> 更新日期: 2026-02-08

## blender_mcp (MCP 服务端)

`src/blender_mcp/` 模块结构:

| 模块 | 职责 |
|------|------|
| `mcp_protocol.py` | MCPServer, JSON-RPC 处理, tools_call 分发 |
| `schemas/tools.py` | 26 工具定义 (TOOL_DEFINITIONS), get_tool() |
| `adapters/` | BlenderAdapter 协议, MockAdapter, SocketAdapter |
| `core/` | 核心基础设施 (guardrails 等) |
| `transport/` | 传输层接口 |
| `catalog/` | 能力目录 |

## blender_mcp_addon (Blender Addon)

`src/blender_mcp_addon/` 模块结构:

| 模块 | 职责 |
|------|------|
| `capabilities/base.py` | 能力分发: 旧能力 + 新 blender.* 能力 |
| `handlers/` | 具体 bpy 操作 (data, nodes, animation, sequencer 等) |
| `handlers/response.py` | 统一响应格式 (_ok/_error) |
| `server/` | TCP Socket 服务器 |
| `operators.py` | Blender UI 操作符 (启动/停止服务器) |
| `preferences.py` | Addon 偏好设置 |
