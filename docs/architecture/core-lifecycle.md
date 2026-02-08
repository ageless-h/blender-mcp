# Core Service Lifecycle

> 更新日期: 2026-02-08

## 启动流程

1. MCPServer 实例化 (`src/blender_mcp/mcp_protocol.py`)
2. 根据 `MCP_ADAPTER` 环境变量选择适配器:
   - `mock` → MockAdapter (测试)
   - 默认 → SocketAdapter (连接 Blender)
3. 加载 TOOL_DEFINITIONS (26 工具) 和 _LEGACY_TOOL_MAP
4. 等待 JSON-RPC `initialize` 请求
5. 进入 ready 状态, 处理 tools/list, tools/call 等

## Blender Addon 侧

1. Addon 注册 (`blender_mcp_addon/__init__.py`)
2. 如果 auto_start=True, 启动 Socket 服务器
3. 接收 MCP 请求 → `execute_capability()` 分发
4. 新 `blender.*` 能力 → `_dispatch_new_capability()`
5. 旧能力 → 直接路由到对应 handler

## 错误处理

- 统一响应格式: `_ok(result=...)` / `_error(code=..., message=...)`
- 所有 handler 异常被 `execute_capability` 捕获
- MCP 层面: 未知工具/方法返回标准 JSON-RPC 错误码
