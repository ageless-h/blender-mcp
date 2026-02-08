# Transport Adapters

> 更新日期: 2026-02-08

## 当前传输方式

| 传输 | 位置 | 说明 |
|------|------|------|
| stdio | examples/stdio_loop.py | 开发/调试用 JSON-line 循环 |
| Socket | src/blender_mcp_addon/server/ | 生产用 TCP socket, Addon 内运行 |
| Mock | src/blender_mcp/adapters/mock.py | 测试用, 可配置响应 |

## Adapter Interface
- `BlenderAdapter` 协议定义于 `src/blender_mcp/adapters/base.py`
- 方法: `execute(capability: str, payload: dict) -> AdapterResult`
- `SocketAdapter` 通过 TCP 连接 Blender Addon
- `MockAdapter` 返回可配置的测试响应

## Future Extensions
WebSocket 传输可通过 `src/blender_mcp/transport/` 接口添加。
