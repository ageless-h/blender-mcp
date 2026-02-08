# Blender MCP 易用性改进待办清单

**目标**：易用性评分从 3.5 星 → 4.5+ 星
**参考项目**：ahujasid/blender-mcp (16.9k ⭐)
**创建日期**：2026-02-08

---

## 🔴 P0 — 立即执行（1-2 周）

### 1. 发布到 PyPI，支持 uvx 安装

> ~~当前状态：未发布，用户需克隆仓库 + 手动设 PYTHONPATH~~
> 当前状态：✅ 已发布 `ageless-blender-mcp 0.1.0` 到 PyPI
> 目标状态：`uvx ageless-blender-mcp` 一行命令即可运行 — ✅ 已达成

- [x] 1.1 `pyproject.toml` 添加 `[project.scripts]` 入口点
  - 文件：`pyproject.toml`
  - 参考：`blender-mcp = "blender_mcp.mcp_protocol:run_mcp_server"`
- [x] 1.2 `pyproject.toml` 补全 `[project]` 元数据（author、license、classifiers、urls）
  - 文件：`pyproject.toml`
- [x] 1.3 确认 `hatchling` 构建产物包含所有必需文件
  - 文件：`pyproject.toml` `[tool.hatch.build]`
- [x] 1.4 本地测试 `uvx` 运行
  - 已构建：`dist/ageless_blender_mcp-0.1.0-py3-none-any.whl`
- [x] 1.5 发布到 TestPyPI 验证
- [x] 1.6 发布到正式 PyPI
  - 已发布：`ageless-blender-mcp 0.1.0` on [PyPI](https://pypi.org/project/ageless-blender-mcp/)
- [x] 1.7 README 更新安装说明为 `uvx blender-mcp`
  - 文件：`README.md`
- [x] 1.8 所有客户端文档更新配置示例
  - 文件：`docs/clients/*.md`（18 个文件）

### 2. 添加策略性使用提示（usage_strategy prompt）

> 当前状态：已有 7 个工作流 prompt，但缺少全局策略引导
> 目标状态：AI 收到 "先读后写、工具选择优先级" 等策略性指引

- [x] 2.1 添加 `blender-usage-strategy` prompt：总体工具使用策略
  - 文件：`src/blender_mcp/prompts/registry.py`
  - 内容：先用感知层了解场景 → 选择正确写入层 → 后备层兜底
- [x] 2.2 添加 `blender-resource-strategy` prompt：资源使用策略
  - 文件：`src/blender_mcp/prompts/registry.py`
  - 内容：可控粒度读取、避免一次取过多数据
- [x] 2.3 添加 `blender-debugging-strategy` prompt：调试策略
  - 文件：`src/blender_mcp/prompts/registry.py`
  - 内容：常见错误排查流程
- [x] 2.4 更新工具概览文档说明 prompt 系统
  - 文件：`docs/tools/overview.md`

### 3. 创建 5 分钟快速开始指南

> 当前状态：无独立快速开始文档，README 中仅有 JSON 示例
> 目标状态：新用户 5 分钟内完成安装 → 连接 → 创建第一个对象

- [x] 3.1 创建 `docs/quick-start.md`
  - 内容：前置条件 → 安装插件 → 配置客户端 → 测试连接 → 创建对象
- [x] 3.2 添加常见故障排除（连接失败、超时、路径错误）
  - 文件：`docs/quick-start.md`
- [x] 3.3 添加验证命令示例（确认连接成功的检查步骤）
  - 文件：`docs/quick-start.md`
- [x] 3.4 README 添加快速开始链接
  - 文件：`README.md`

### 4. 添加错误重试和自动重连

> 当前状态：SocketAdapter 单次连接，超时返回 `adapter_timeout` 错误码
> 目标状态：自动重试 + 自动重连 + 用户友好错误消息

- [x] 4.1 SocketAdapter 添加重试逻辑（指数退避，默认 3 次）
  - 文件：`src/blender_mcp/adapters/socket.py`
- [x] 4.2 MCPServer.tools_call 添加连接失败自动重连
  - 文件：`src/blender_mcp/mcp_protocol.py`
- [x] 4.3 错误消息从技术码改为用户友好文本
  - `adapter_timeout` → "命令超时，请尝试简化请求或分步执行"
  - `adapter_unavailable` → "无法连接 Blender，请确认插件已启动并检查端口"
  - `adapter_empty_response` → "Blender 返回空响应，请检查插件状态"
  - 文件：`src/blender_mcp/adapters/socket.py`
- [x] 4.4 添加重试和重连的单元测试
  - 文件：`tests/test_adapters.py`

---

## 🟡 P1 — 短期执行（1-2 月）

### 5. 添加 Blender 侧边栏面板（VIEW3D）

> 当前状态：仅有偏好设置面板（Edit > Preferences），无侧边栏
> 目标状态：按 N 键可在 3D 视口侧边栏看到连接状态和控制按钮

- [x] 5.1 创建侧边栏面板类 `BlenderMCPPanel`（VIEW3D_PT）
  - 文件：新建 `src/blender_mcp_addon/ui.py`
- [x] 5.2 添加 `BlenderMCPProperties` 属性组（连接状态等运行时属性）
  - 文件：`src/blender_mcp_addon/ui.py`
- [x] 5.3 面板显示：连接状态指示、启动/停止按钮、主机端口配置
  - 文件：`src/blender_mcp_addon/ui.py`
- [x] 5.4 在 `__init__.py` 注册新 UI 类
  - 文件：`src/blender_mcp_addon/__init__.py`

### 6. 增强日志系统

> 当前状态：有 logging.getLogger 但日志输出不够详细
> 目标状态：每个关键步骤有日志，错误带恢复建议

- [x] 6.1 MCP 服务器启动时输出配置信息日志
  - 文件：`src/blender_mcp/mcp_protocol.py`
- [x] 6.2 每次工具调用记录 INFO 日志（工具名、参数摘要、耗时）
  - 文件：`src/blender_mcp/mcp_protocol.py`
- [x] 6.3 Socket 连接/断开/重试记录 DEBUG 日志
  - 文件：`src/blender_mcp/adapters/socket.py`
- [x] 6.4 支持通过环境变量 `MCP_LOG_LEVEL` 控制日志级别
  - 文件：`src/blender_mcp/mcp_protocol.py`

---

## 🟢 P2 — 长期执行（3-6 月）

### 8. 实现遥测系统（可选，隐私保护）

> 当前状态：无遥测
> 目标状态：可选的匿名使用统计，用户完全控制开关

- [x] 8.1 创建遥测模块
  - 文件：新建 `src/blender_mcp/telemetry.py`
- [x] 8.2 实现 `telemetry_tool` 装饰器（自动记录成功/失败/耗时）
  - 文件：`src/blender_mcp/telemetry.py`
- [x] 8.3 支持环境变量 `DISABLE_TELEMETRY=true` 完全禁用
  - 文件：`src/blender_mcp/telemetry.py`
- [ ] 8.4 Blender 插件侧边栏添加遥测同意复选框（通过 MCP_TELEMETRY 环境变量控制）
  - 文件：`src/blender_mcp_addon/ui.py`
  - ⚠️ 当前 ui.py 中无遥测 UI，仅通过环境变量控制

### 9. 多平台一键安装

> 当前状态：无深度链接
> 目标状态：Cursor / VS Code / Windsurf/以及其他Z:\8_code\blender-mcp\docs\clients中的客户端 一键安装按钮

- [ ] 9.1 添加 Cursor 一键安装深度链接
  - `README.md` ✅ 已有 deeplink 按钮
  - `docs/clients/cursor.md` ❌ 未添加 deeplink
- [ ] 9.2 添加 VS Code 一键安装协议链接
  - `README.md` ✅ 已有 deeplink 按钮
  - `docs/clients/vs-code-copilot.md` ❌ 未添加 deeplink
- [ ] 9.3 更新其他客户端文档添加简化配置
  - 文件：`docs/clients/*.md`
- [ ] 9.4 更多客户端支持
  - 文件：需要添加的客户端文档

### 10. 社区建设

> 当前状态：仅有 CI workflow，无 issue 模板和贡献指南
> 目标状态：完善的社区协作基础设施

- [x] 10.1 创建 GitHub Issue 模板（bug report / feature request）
  - 文件：新建 `.github/ISSUE_TEMPLATE/`
- [x] 10.2 创建 Pull Request 模板
  - 文件：新建 `.github/PULL_REQUEST_TEMPLATE.md`
- [x] 10.3 创建贡献指南
  - 文件：新建 `CONTRIBUTING.md`
- [x] 10.4 README 添加 Star 历史徽章
  - 文件：`README.md`

---

## 里程碑

| 里程碑 | 目标评分 | 完成标志 |
|--------|---------|---------|
| M1（1-2 周） | 4.0 星 | P0 全部完成：PyPI + 策略 prompt + 快速开始 + 错误重试 |
| M2（1-2 月） | 4.5 星 | P1 全部完成：侧边栏 UI + 日志增强 + 视频教程 |
| M3（3-6 月） | 4.8 星 | P2 全部完成：遥测 + 一键安装 + 社区基建 |

