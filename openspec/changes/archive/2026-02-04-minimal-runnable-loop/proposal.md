## Why

当前系统缺少可运行的最小链路：MCPServer 尚未接入真实 stdio 传输、审计日志缺少实际实现、allowlist 的更新未被审计。这导致最小验证闭环不可用，需要补齐关键运行路径。

## What Changes

- MCPServer 接入真实 stdio transport，形成最小可运行通信路径。
- 提供基础 audit logger 实现（内存与文件/JSON 可导出）。
- allowlist 更新写入审计日志，满足安全要求。
- 补齐 README/AGENTS 与 project.md 的最小运行与协作入口说明。
- 提供最小可运行示例与脚本。
- 为 rate limit 增加时间窗口语义。
- 提供插件端最小可用实现。

## Capabilities

### New Capabilities
- `stdio-transport`: MCPServer 的 stdio 传输接入与最小通信闭环。
- `audit-logger-implementation`: 审计日志的基础实现与导出能力。
- `allowlist-audit`: allowlist 更新的审计记录与可追溯性。
- `validation-gate-ci`: integration 示例可运行与最小 CI 结构规范。
- `readme-entrypoint`: README 的最小运行入口与使用说明。
- `agents-guidance`: AGENTS 协作与执行指南。
- `project-conventions`: OpenSpec project.md 的工程约定落地。
- `rate-limit-window`: rate limit 的时间窗口语义。
- `addon-minimal-implementation`: 插件端最小可用实现。
- `runnable-examples`: 可运行示例与脚本规范。

### Modified Capabilities
- None.

## Impact

- MCPServer 具备最小可运行链路。
- 审计与 allowlist 更新具备可追溯性。
- integration 示例与 CI 具备最小验证闭环。
- 文档入口与工程约定形成最小可执行说明。
