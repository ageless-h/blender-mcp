# Blender MCP

[English](#english) | [中文](#中文)

<!-- Badges -->
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/ageless-h/blender-mcp/releases)
[![Blender](https://img.shields.io/badge/Blender-4.2%2B-orange.svg)](https://www.blender.org/)
[![MCP](https://img.shields.io/badge/MCP-2024--11--05-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/ageless-blender-mcp.svg)](https://pypi.org/project/ageless-blender-mcp/)



---

<a name="english"></a>
## English

MCP server integration for AI-assisted Blender automation.

### Layered Tool Architecture

Blender MCP uses a **four-layer tool architecture** with **26 specialized tools** organized by intent:

| Layer | Tool Count | Purpose |
|-------|-----------|---------|
| **Perception** | 11 tools | Read Blender state deeply with controllable granularity |
| **Declarative Write** | 3 tools | Node editor (6 contexts) + Animation + VSE Sequencer |
| **Imperative Write** | 9 tools | Object/Material/Modifier/UV/Constraint/Physics/Scene |
| **Fallback** | 3 tools | execute_operator + execute_script + import_export |

**Perception Layer (11 tools)**:
| Tool | Description |
|------|-------------|
| `blender_get_objects` | List/scene objects with filters |
| `blender_get_object_data` | Deep object data (12 include options) |
| `blender_get_node_tree` | Read any node tree (6 contexts) |
| `blender_get_animation_data` | Keyframes/NLA/drivers/shape keys |
| `blender_get_materials` | Material asset list |
| `blender_get_scene` | Scene-level global info |
| `blender_get_collections` | Collection hierarchy tree |
| `blender_get_armature_data` | Armature/bone hierarchy/constraints/poses |
| `blender_get_images` | Texture/image asset list |
| `blender_capture_viewport` | Viewport screenshot |
| `blender_get_selection` | Current selection/mode/active object |

**Declarative Write Layer (3 tools)**:
| Tool | Description |
|------|-------------|
| `blender_edit_nodes` | Edit any node tree (add/remove/connect/disconnect/set_value) ⭐ Core |
| `blender_edit_animation` | Edit animation (keyframe/NLA/driver/shape_key/frame_range) |
| `blender_edit_sequencer` | Edit VSE video sequence (strip/transition/effect) |

**Imperative Write Layer (9 tools)**:
| Tool | Description |
|------|-------------|
| `blender_create_object` | Create scene objects (MESH/LIGHT/CAMERA/CURVE/EMPTY/ARMATURE/TEXT) |
| `blender_modify_object` | Transform/parent/visibility/rename/delete |
| `blender_manage_material` | Material create/PBR edit/assign/duplicate/delete |
| `blender_manage_modifier` | Modifier add/configure/apply/delete/reorder |
| `blender_manage_collection` | Collection create/delete/object link/hierarchy/visibility |
| `blender_manage_uv` | UV unwrap/seam/pack/layer management |
| `blender_manage_constraints` | Object/bone constraint add/configure/delete |
| `blender_manage_physics` | Physics simulation add/configure/bake |
| `blender_setup_scene` | Render engine/world environment/timeline config |

**Fallback Layer (3 tools)**:
| Tool | Description |
|------|-------------|
| `blender_execute_operator` | Execute any bpy.ops.* operator |
| `blender_execute_script` | Execute arbitrary Python code (⚠️ use with caution) |
| `blender_import_export` | Import/export asset files (FBX/OBJ/GLTF/USD/Alembic/STL/etc.) |

> **Note**: All tools use `blender_` prefix to avoid conflicts in multi-server environments. Tool names follow MCP specification with underscores. Payload wrapper is removed - all parameters are exposed directly as top-level inputSchema properties.

**Tool Naming**: All tools use the `blender_` prefix to avoid conflicts in multi-server environments.

### Quick Start

> **New to Blender MCP?** See the [5-Minute Quick Start Guide](docs/quick-start.md) for step-by-step setup instructions.

```json
// Create a cube
{
  "name": "MyCube",
  "object_type": "MESH",
  "primitive": "cube",
  "size": 2.0
}

// Move it
{
  "name": "MyCube",
  "location": [1, 2, 3]
}

// Add a subdivision modifier
{
  "action": "add",
  "object_name": "MyCube",
  "modifier_name": "Subdivision",
  "modifier_type": "SUBSURF",
  "settings": {"levels": 2}
}

// Read object data
{
  "name": "MyCube",
  "include": ["summary", "modifiers"]
}

// Capture viewport
{
  "shading": "SOLID",
  "format": "PNG"
}
```

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
# Recommended: one-line install & run
uvx ageless-blender-mcp

# Or install globally
pip install ageless-blender-mcp
blender-mcp

# Or from source
uv sync
python -m blender_mcp.mcp_protocol
```

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

### 分层工具架构

Blender MCP 采用**四层工具架构**，**26 个专用工具**按意图组织：

| 层级 | 工具数量 | 用途 |
|------|---------|------|
| **感知层** | 11 个工具 | 以可控粒度深度读取 Blender 状态 |
| **声明式写入层** | 3 个工具 | 节点编辑器（6种上下文）+ 动画 + VSE 序列编辑器 |
| **命令式写入层** | 9 个工具 | 对象/材质/修改器/UV/约束/物理/场景 |
| **后备层** | 3 个工具 | execute_operator + execute_script + import_export |

**感知层（11 个工具）**：
| 工具 | 描述 |
|------|------|
| `blender_get_objects` | 列出/筛选场景对象 |
| `blender_get_object_data` | 单对象深度数据（12 种 include 选项） |
| `blender_get_node_tree` | 读取任意节点树（6 种上下文） |
| `blender_get_animation_data` | 关键帧/NLA/驱动器/形态键 |
| `blender_get_materials` | 材质资产列表 |
| `blender_get_scene` | 场景级全局信息 |
| `blender_get_collections` | 集合层级树 |
| `blender_get_armature_data` | 骨架/骨骼层级/约束/姿态 |
| `blender_get_images` | 纹理/图片资产列表 |
| `blender_capture_viewport` | 视口截图 |
| `blender_get_selection` | 当前选择/模式/活动对象 |

**声明式写入层（3 个工具）**：
| 工具 | 描述 |
|------|------|
| `blender_edit_nodes` | 编辑任意节点树（添加/移除/连接/断开/设置值）⭐ 核心 |
| `blender_edit_animation` | 编辑动画（关键帧/NLA/驱动器/形态键/帧范围） |
| `blender_edit_sequencer` | 编辑 VSE 视频序列（片段/转场/特效） |

**命令式写入层（9 个工具）**：
| 工具 | 描述 |
|------|------|
| `blender_create_object` | 创建场景对象（MESH/LIGHT/CAMERA/CURVE/EMPTY/ARMATURE/TEXT） |
| `blender_modify_object` | 变换/父子/可见性/重命名/删除 |
| `blender_manage_material` | 材质创建/PBR 编辑/赋予/复制/删除 |
| `blender_manage_modifier` | 修改器添加/配置/应用/删除/排序 |
| `blender_manage_collection` | 集合创建/删除/对象链接/层级/可见性 |
| `blender_manage_uv` | UV 展开/缝合线/打包/图层管理 |
| `blender_manage_constraints` | 对象/骨骼约束添加/配置/删除 |
| `blender_manage_physics` | 物理模拟添加/配置/烘焙 |
| `blender_setup_scene` | 渲染引擎/世界环境/时间线配置 |

**后备层（3 个工具）**：
| 工具 | 描述 |
|------|------|
| `blender_execute_operator` | 执行任意 bpy.ops.* 操作符 |
| `blender_execute_script` | 执行任意 Python 代码（⚠️ 谨慎使用） |
| `blender_import_export` | 导入/导出资产文件（FBX/OBJ/GLTF/USD/Alembic/STL 等） |

> **注意**: 所有工具使用 `blender_` 前缀以避免多服务器环境下的命名冲突。工具名称符合 MCP 规范使用下划线。Payload 包装层已移除 - 所有参数直接暴露为顶层 inputSchema 属性。

**工具命名**: 所有工具使用 `blender_` 前缀以避免多服务器环境下的命名冲突。

### 快速开始

> **初次使用？** 请参阅 [5 分钟快速开始指南](docs/quick-start.md) 获取详细安装步骤。

```json
// 创建一个立方体
{
  "name": "MyCube",
  "object_type": "MESH",
  "primitive": "cube",
  "size": 2.0
}

// 移动它
{
  "name": "MyCube",
  "location": [1, 2, 3]
}

// 添加细分修改器
{
  "action": "add",
  "object_name": "MyCube",
  "modifier_name": "Subdivision",
  "modifier_type": "SUBSURF",
  "settings": {"levels": 2}
}

// 读取对象数据
{
  "name": "MyCube",
  "include": ["summary", "modifiers"]
}

// 捕获视口
{
  "shading": "SOLID",
  "format": "PNG"
}
```

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
# 推荐：一行命令安装并运行
uvx ageless-blender-mcp

# 或全局安装
pip install ageless-blender-mcp
blender-mcp

# 或从源码
uv sync
python -m blender_mcp.mcp_protocol
```

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

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ageless-h/blender-mcp&type=Date)](https://star-history.com/#ageless-h/blender-mcp&Date)

## License

MIT License - see [LICENSE](LICENSE) for details.
