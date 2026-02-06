# Blender MCP

[English](#english) | [中文](#中文)

<!-- Badges -->
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/ageless-h/blender-mcp/releases)
[![Blender](https://img.shields.io/badge/Blender-4.2%2B-orange.svg)](https://www.blender.org/)
[![MCP](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

<!-- Package Registry Placeholders -->
<!--
[![PyPI](https://img.shields.io/pypi/v/blender-mcp.svg)](https://pypi.org/project/blender-mcp/)
[![npm](https://img.shields.io/npm/v/blender-mcp.svg)](https://www.npmjs.com/package/blender-mcp)
-->

---

<a name="english"></a>
## English

MCP server integration for AI-assisted Blender automation.

### Unified Tool Architecture

Blender MCP uses a highly compressed tool architecture with **8 core tools** that cover 99.9% of Blender functionality:

| Tool | Description |
|------|-------------|
| `data.create` | Create any Blender data block (objects, meshes, materials, etc.) |
| `data.read` | Read properties from any data block |
| `data.write` | Write properties to any data block |
| `data.delete` | Delete data blocks |
| `data.list` | List all data blocks of a type |
| `data.link` | Link/unlink data blocks (e.g., object to collection) |
| `operator.execute` | Execute any Blender operator (bpy.ops.*) |
| `info.query` | Query status, history, statistics, and viewport capture |

**Optional (disabled by default):**
- `script.execute` - Execute arbitrary Python code (requires explicit enablement)

### Quick Start

```json
// Create a cube
{"capability": "data.create", "payload": {"type": "object", "name": "MyCube", "params": {"object_type": "MESH"}}}

// Move it
{"capability": "data.write", "payload": {"type": "object", "name": "MyCube", "properties": {"location": [1, 2, 3]}}}

// Add a subdivision modifier
{"capability": "operator.execute", "payload": {"operator": "object.modifier_add", "params": {"type": "SUBSURF"}}}
```

See [docs/migration/tools-migration.md](docs/migration/tools-migration.md) for detailed documentation.

### Installation

#### Blender Addon

1. Copy or symlink `src/blender_mcp_addon/` to your Blender addons folder:
   - Windows: `%APPDATA%\Blender\<version>\scripts\addons\blender_mcp_addon`
   - macOS: `~/Library/Application Support/Blender/<version>/scripts/addons/blender_mcp_addon`
   - Linux: `~/.config/blender/<version>/scripts/addons/blender_mcp_addon`

2. In Blender: Edit > Preferences > Add-ons > Search "Blender MCP" > Enable

3. Configure and click "Start Server"

#### MCP Server

```bash
# Install
uv sync  # or pip install .

# Run
python -m blender_mcp.mcp_protocol
```

<!-- Package Installation (Coming Soon)
```bash
pip install blender-mcp
```
-->

### Supported MCP Clients

<details>
<summary>Click to expand client list</summary>

| Client | Documentation |
|--------|---------------|
| Amp | [docs/clients/amp.md](docs/clients/amp.md) |
| Antigravity | [docs/clients/antigravity.md](docs/clients/antigravity.md) |
| Claude Code | [docs/clients/claude-code.md](docs/clients/claude-code.md) |
| Cline | [docs/clients/cline.md](docs/clients/cline.md) |
| Codex | [docs/clients/codex.md](docs/clients/codex.md) |
| Copilot CLI | [docs/clients/copilot-cli.md](docs/clients/copilot-cli.md) |
| Copilot / VS Code | [docs/clients/vs-code-copilot.md](docs/clients/vs-code-copilot.md) |
| Cursor | [docs/clients/cursor.md](docs/clients/cursor.md) |
| Factory CLI | [docs/clients/factory-cli.md](docs/clients/factory-cli.md) |
| Gemini CLI | [docs/clients/gemini-cli.md](docs/clients/gemini-cli.md) |
| Gemini Code Assist | [docs/clients/gemini-code-assist.md](docs/clients/gemini-code-assist.md) |
| JetBrains AI Assistant | [docs/clients/jetbrains.md](docs/clients/jetbrains.md) |
| Kiro | [docs/clients/kiro.md](docs/clients/kiro.md) |
| OpenCode | [docs/clients/opencode.md](docs/clients/opencode.md) |
| Qoder | [docs/clients/qoder.md](docs/clients/qoder.md) |
| Visual Studio | [docs/clients/visual-studio.md](docs/clients/visual-studio.md) |
| Warp | [docs/clients/warp.md](docs/clients/warp.md) |
| Windsurf | [docs/clients/windsurf.md](docs/clients/windsurf.md) |

</details>

### Version Compatibility

| Blender Version | Status |
|-----------------|--------|
| 4.2 LTS | ✅ Supported |
| 4.5 LTS | ✅ Supported |
| 5.0+ | ✅ Supported |
| < 4.2 | ❌ Not Supported |

See [docs/versioning/support-matrix.md](docs/versioning/support-matrix.md) for details.

---

<a name="中文"></a>
## 中文

用于 AI 辅助 Blender 自动化的 MCP 服务器集成。

### 统一工具架构

Blender MCP 采用高度压缩的工具架构，**8 个核心工具** 覆盖 99.9% 的 Blender 功能：

| 工具 | 描述 |
|------|------|
| `data.create` | 创建任何 Blender 数据块（对象、网格、材质等） |
| `data.read` | 读取任何数据块的属性 |
| `data.write` | 写入任何数据块的属性 |
| `data.delete` | 删除数据块 |
| `data.list` | 列出某类型的所有数据块 |
| `data.link` | 链接/取消链接数据块（如将对象链接到集合） |
| `operator.execute` | 执行任何 Blender 操作符 (bpy.ops.*) |
| `info.query` | 查询状态、历史、统计信息和视口截图 |

**可选（默认禁用）：**
- `script.execute` - 执行任意 Python 代码（需要明确启用）

### 快速开始

```json
// 创建一个立方体
{"capability": "data.create", "payload": {"type": "object", "name": "MyCube", "params": {"object_type": "MESH"}}}

// 移动它
{"capability": "data.write", "payload": {"type": "object", "name": "MyCube", "properties": {"location": [1, 2, 3]}}}

// 添加细分修改器
{"capability": "operator.execute", "payload": {"operator": "object.modifier_add", "params": {"type": "SUBSURF"}}}
```

详见 [docs/migration/tools-migration.md](docs/migration/tools-migration.md)。

### 安装

#### Blender 插件

1. 将 `src/blender_mcp_addon/` 复制或符号链接到 Blender 插件目录：
   - Windows: `%APPDATA%\Blender\<版本>\scripts\addons\blender_mcp_addon`
   - macOS: `~/Library/Application Support/Blender/<版本>/scripts/addons/blender_mcp_addon`
   - Linux: `~/.config/blender/<版本>/scripts/addons/blender_mcp_addon`

2. 在 Blender 中：编辑 > 偏好设置 > 插件 > 搜索 "Blender MCP" > 启用

3. 配置后点击 "启动服务器"

#### MCP 服务器

```bash
# 安装
uv sync  # 或 pip install .

# 运行
python -m blender_mcp.mcp_protocol
```

<!-- 包安装（即将推出）
```bash
pip install blender-mcp
```
-->

### 支持的 MCP 客户端

<details>
<summary>点击展开客户端列表</summary>

| 客户端 | 文档 |
|--------|------|
| Amp | [docs/clients/amp.md](docs/clients/amp.md) |
| Antigravity | [docs/clients/antigravity.md](docs/clients/antigravity.md) |
| Claude Code | [docs/clients/claude-code.md](docs/clients/claude-code.md) |
| Cline | [docs/clients/cline.md](docs/clients/cline.md) |
| Codex | [docs/clients/codex.md](docs/clients/codex.md) |
| Copilot CLI | [docs/clients/copilot-cli.md](docs/clients/copilot-cli.md) |
| Copilot / VS Code | [docs/clients/vs-code-copilot.md](docs/clients/vs-code-copilot.md) |
| Cursor | [docs/clients/cursor.md](docs/clients/cursor.md) |
| Factory CLI | [docs/clients/factory-cli.md](docs/clients/factory-cli.md) |
| Gemini CLI | [docs/clients/gemini-cli.md](docs/clients/gemini-cli.md) |
| Gemini Code Assist | [docs/clients/gemini-code-assist.md](docs/clients/gemini-code-assist.md) |
| JetBrains AI 助手 | [docs/clients/jetbrains.md](docs/clients/jetbrains.md) |
| Kiro | [docs/clients/kiro.md](docs/clients/kiro.md) |
| OpenCode | [docs/clients/opencode.md](docs/clients/opencode.md) |
| Qoder | [docs/clients/qoder.md](docs/clients/qoder.md) |
| Visual Studio | [docs/clients/visual-studio.md](docs/clients/visual-studio.md) |
| Warp | [docs/clients/warp.md](docs/clients/warp.md) |
| Windsurf | [docs/clients/windsurf.md](docs/clients/windsurf.md) |

</details>

### 版本兼容性

| Blender 版本 | 状态 |
|-------------|------|
| 4.2 LTS | ✅ 支持 |
| 4.5 LTS | ✅ 支持 |
| 5.0+ | ✅ 支持 |
| < 4.2 | ❌ 不支持 |

详见 [docs/versioning/support-matrix.md](docs/versioning/support-matrix.md)。

---

## License

MIT License - see [LICENSE](LICENSE) for details.
