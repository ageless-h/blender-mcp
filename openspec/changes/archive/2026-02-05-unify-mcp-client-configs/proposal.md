## Why

项目目前仅在 README.md 中提供了通用的 `.mcp.json` 配置示例，但不同的 MCP 客户端（如 Cursor、Claude Code、VS Code Copilot 等）有各自不同的配置方式和路径。用户需要针对其使用的特定客户端的明确配置指南，同时需要测试来验证 MCP 能够正常注册和工作。

## What Changes

- 添加针对 20 种主流 MCP 客户端的配置文档，涵盖：Amp, Antigravity, Claude Code, Cline, Codex, Copilot CLI, Copilot / VS Code, Cursor, Factory CLI, Gemini CLI, Gemini Code Assist, JetBrains AI Assistant & Junie, Kiro, OpenCode, Qoder, Qoder CLI, Visual Studio, Warp, Windsurf
- 创建 MCP 注册验证测试，确保 `tools/list` 和 `initialize` 能正确响应
- 统一项目中现有的 MCP 配置相关描述（README.md, examples/README.md）
- 提供每个客户端的配置文件位置、格式和验证步骤

## Capabilities

### New Capabilities
- `mcp-client-config-docs`: 针对所有主流 MCP 客户端的配置文档，包含配置文件位置、格式示例、验证步骤
- `mcp-registration-testing`: MCP 注册功能的自动化测试，验证 `initialize` 和 `tools/list` 响应正确性

### Modified Capabilities
（无现有 spec 需要修改，此变更主要是新增文档和测试）

## Impact

- **文档**: README.md 将更新 MCP Client Configuration 章节，新增 `docs/clients/` 目录存放各客户端配置指南
- **测试**: 新增 `tests/mcp/test_registration.py` 验证 MCP 协议注册流程
- **示例**: 更新 `examples/README.md` 与新文档保持一致
- **依赖**: 无新增依赖

