## Why

当前实现与协议/边界/版本规范存在偏差：JSON-RPC 2.0 语义未落地、边界验证与兼容性脚本缺失、支持矩阵数据未落地、Guardrails 未在请求入口强制执行。这些问题阻断“可扩展阶段”的可靠性。

## What Changes

- 落地 JSON-RPC 2.0 最小语义处理或回退到“最小 JSON 行协议”的规范调整。
- 补齐插件边界验证脚本与兼容性检查脚本。
- 落地支持矩阵与兼容性结果数据文件。
- 将 Guardrails 接入核心请求链路实现执行前阻断。

## Capabilities

### New Capabilities
- `jsonrpc-minimal-handling`: JSON-RPC 2.0 最小字段处理与错误语义。
- `compatibility-execution-assets`: 兼容性执行脚本与数据文件落地。
- `plugin-boundary-validation`: 插件边界验证脚本与执行流程。

### Modified Capabilities
- `protocol-freeze`: 根据实际实现冻结协议语义（JSON-RPC 或最小 JSON 行协议）。
- `resource-guardrails-strategy`: 强制接入核心请求链路并形成阻断点。

## Impact

- MCPServer 传输处理、脚本与版本数据文件将变更。
- 文档与规范需要与最终协议选择保持一致。
