# Integration Test Plan

> 更新日期: 2026-02-08

## 测试结构

| 目录 | 文件数 | 测试数 | 说明 |
|------|--------|--------|------|
| tests/ | 12 | 72 | 核心: 协议, 适配器, guardrails, Schema, 错误码 |
| tests/tools/ | 5 | 164 | 26 工具单测 + Schema 验证 |
| tests/mcp/ | 1 | 14 | MCP 注册: 工具数量/前缀/注解 |
| tests/integration/ | 2 | 21 | E2E 流程 + 工作流测试 |
| **总计** | **20** | **271** | 全部通过 |

## 运行命令

```bash
# 全部测试
uv run python -m unittest discover -s tests -p "test_*.py"

# 仅工具测试
uv run python -m unittest discover -s tests/tools -p "test_*.py"

# 仅 E2E 测试
uv run python -m unittest tests.integration.test_e2e_flow
```

## 测试场景

### 协议层 (tests/test_mcp_protocol.py)
- initialize 返回正确的 capabilities
- tools/list 返回 26 个工具
- tools/call 成功调用 + 错误处理
- prompts/list 和 prompts/get
- 未知方法返回 MethodNotFound

### 工具层 (tests/tools/)
- 感知层 11 工具: 各参数组合调用成功
- 声明式层 3 工具: 多种操作类型
- 命令式层 9 工具: 各 action 调用成功
- 后备层 3 工具: operator/script/import_export
- Schema 验证: 结构/注解/枚举/required

### E2E 流程 (tests/integration/test_e2e_flow.py)
- initialize → tools/list → tools/call 完整流程
- JSON-RPC 版本和 ID 匹配
- 旧工具名称兼容
- 通知不产生响应
- 未知工具/方法返回错误

## Environment
- 默认: MCP_ADAPTER=mock (MockAdapter)
- 真实 Blender: tests/integration/real_blender/ (需 opt-in)
