## Context

Blender MCP 项目需要支持多种 MCP 客户端，每个客户端有不同的配置文件位置和格式。当前仅在 README.md 提供通用示例，用户需要自行研究各客户端的配置方式。本设计解决文档组织和测试验证两个问题。

**当前状态**:
- README.md 第 59-78 行包含通用 `.mcp.json` 配置示例
- 项目根目录有 `.mcp.json` 示例文件
- 无针对特定客户端的配置指南
- 无 MCP 注册流程的自动化测试

**目标客户端列表** (20 种):
Amp, Antigravity, Claude Code, Cline, Codex, Copilot CLI, Copilot / VS Code, Cursor, Factory CLI, Gemini CLI, Gemini Code Assist, JetBrains AI Assistant & Junie, Kiro, OpenCode, Qoder, Qoder CLI, Visual Studio, Warp, Windsurf

## Goals / Non-Goals

**Goals:**
- 为每种 MCP 客户端提供可复制粘贴的配置示例
- 统一配置文档的格式和结构
- 验证 MCP 注册流程（`initialize` 和 `tools/list`）能正常工作
- README.md 提供快速入口，详细文档在独立文件中

**Non-Goals:**
- 不负责各客户端的安装指南（假设用户已安装客户端）
- 不提供客户端特定功能的使用教程
- 不覆盖非主流或实验性 MCP 客户端

## Decisions

### D1: 文档组织结构

**决定**: 在 `docs/clients/` 目录下为每个客户端创建独立 Markdown 文件

**理由**:
- 单文件便于独立维护和更新
- 避免 README.md 过长
- 文件名采用 kebab-case（如 `claude-code.md`），便于 URL 链接

**替代方案**:
- 全部放入 README.md → 文件过长，难以维护
- 单个 `docs/mcp-clients.md` → 客户端更新时易冲突

### D2: 配置文档标准化模板

**决定**: 每个客户端文档采用统一结构

```markdown
# {Client Name} Configuration

## Config File Location
- Windows: `...`
- macOS: `...`
- Linux: `...`

## Configuration

\```json
{
  "mcpServers": {
    "blender": { ... }
  }
}
\```

## Verification
1. 打开客户端
2. 检查 MCP 服务器列表
3. 测试 tools/list 响应

## Troubleshooting
- 常见问题及解决方案
```

**理由**: 统一格式让用户快速找到所需信息，便于维护

### D3: MCP 注册测试设计

**决定**: 在 `tests/mcp/test_registration.py` 中创建测试，使用 subprocess 调用 MCP 协议模块

**测试内容**:
1. `initialize` 请求返回正确的 `serverInfo` 和 `capabilities`
2. `tools/list` 返回非空工具列表
3. 响应符合 JSON-RPC 2.0 格式

**理由**: 
- 使用 subprocess 模拟真实客户端调用方式
- 不依赖特定客户端，通用性强

### D4: README.md 更新策略

**决定**: README.md 保留简化的通用配置示例，添加链接指向 `docs/clients/`

**理由**: 保持 README 简洁，同时提供详细文档入口

## Risks / Trade-offs

**[R1] 客户端配置可能随版本更新变化** → 在文档中标注测试时的客户端版本，定期检查更新

**[R2] 部分客户端配置信息难以验证** → 优先覆盖可验证的主流客户端，标注未验证的配置为"社区贡献"

**[R3] 维护 20 个文档的工作量** → 采用统一模板减少差异，优先完成使用量高的客户端（Cursor, Claude Code, VS Code）

