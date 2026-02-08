# Top-Level Layout

> 更新日期: 2026-02-08

## Layout

| 目录 | 说明 |
|------|------|
| `src/blender_mcp/` | MCP 服务端: 协议处理, Schema 定义, 适配器 |
| `src/blender_mcp_addon/` | Blender Addon: bpy 操作, handlers, Socket 服务器 |
| `docs/` | 项目文档 (架构/工具/安全/测试等) |
| `openspec/` | OpenSpec changes, specs, archives |
| `tests/` | 自动化测试 (271 tests) |
| `tests/tools/` | 26 工具单元测试 + Schema 验证 |
| `tests/integration/` | E2E 集成测试 |
| `tests/mcp/` | MCP 协议注册测试 |
| `examples/` | 可运行示例 (stdio_loop) |
| `scripts/` | 开发脚本和维护工具 |

## Rules
- Each top-level directory MUST have a short README describing ownership and scope.
- New top-level directories require an update to this document.
