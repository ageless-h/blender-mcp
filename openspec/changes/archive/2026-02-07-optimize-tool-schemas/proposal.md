## Why

当前 MCP 工具架构存在三个根本性问题：

1. **Schema 黑盒**：所有工具的 `inputSchema` 仅定义一个 `payload` 对象，无任何参数描述、类型约束或 enum 值。LLM 无法从 schema 推断正确的参数结构，首次调用成功率极低（估计 <30%）。

2. **工具粒度错配**：当前 8 个工具（data.create/read/write/delete/list/link + operator.execute + info.query）按 API 结构划分，不按用户意图划分。LLM 需要先理解内部 DataType 枚举和 payload 嵌套结构才能使用，学习成本高。

3. **能力覆盖不足**：缺少对节点编辑（着色器/合成器/几何节点）、动画、VSE 视频序列、UV 映射、约束、物理模拟等 Blender 核心工作域的专用支持。

## What Changes

### 设计哲学

从"API 映射"转变为"感知-声明式-命令式"三层架构：

- **感知层**（Read）：大量读取工具让 LLM 深入理解 Blender 当前状态
- **声明式写入层**：通过节点编辑器和时间轴两种 LLM 友好的声明式接口完成复杂创作
- **命令式写入层**：精简、可复用的对象/场景操作工具
- **后备层**：execute_operator / execute_script / import_export 覆盖长尾需求

### 具体变更

- **展平 payload**：移除 `payload` 包装层，所有参数直接暴露为顶层 inputSchema 属性
- **手写全部 Schema**：为每个工具编写详细的 JSON Schema，包含 description、enum、default、minimum/maximum 等约束
- **工具重新划分**：从 8 个 API 映射工具 → 26 个意图驱动工具
- **新增工具注解**：为每个工具标注 readOnlyHint、destructiveHint、idempotentHint
- **新增 blender_ 前缀**：避免多 MCP 服务器环境下的工具名冲突

### 工具列表（26 个）

**感知层（11 个）**：
- `blender_get_objects` — 列出/筛选场景对象
- `blender_get_object_data` — 单对象深度数据（12 种 include 选项）
- `blender_get_node_tree` — 读取任意节点树（6 种上下文：Object Shader / World Shader / LineStyle Shader / Compositor / GN Modifier / GN Tool）
- `blender_get_animation_data` — 关键帧/NLA/驱动器/形态键
- `blender_get_materials` — 材质资产列表
- `blender_get_scene` — 场景全局信息（统计/渲染/世界/时间线/版本）
- `blender_get_collections` — 集合层级树
- `blender_get_armature_data` — 骨架/骨骼层级/约束/姿态
- `blender_get_images` — 纹理/图片资产列表
- `blender_capture_viewport` — 视口截图
- `blender_get_selection` — 当前选择/模式/活动对象

**声明式写入层（3 个）**：
- `blender_edit_nodes` — 编辑任意节点树（add/remove/connect/disconnect/set_value）⭐ 核心工具
- `blender_edit_animation` — 编辑动画数据（keyframe/NLA/driver/shape_key/frame_range）
- `blender_edit_sequencer` — 编辑 VSE 视频序列（strip/transition/effect）

**命令式写入层（9 个）**：
- `blender_create_object` — 创建场景对象（MESH/LIGHT/CAMERA/CURVE/EMPTY/ARMATURE/TEXT）
- `blender_modify_object` — 变换/父子/可见性/重命名/删除
- `blender_manage_material` — 材质创建/PBR 编辑/赋予/复制/删除
- `blender_manage_modifier` — 修改器添加/配置/应用/删除/排序
- `blender_manage_collection` — 集合创建/删除/对象链接/层级/可见性
- `blender_manage_uv` — UV 展开/缝合线/打包/图层管理
- `blender_manage_constraints` — 对象/骨骼约束添加/配置/删除
- `blender_manage_physics` — 物理模拟添加/配置/烘焙
- `blender_setup_scene` — 渲染引擎/世界环境/时间线配置

**后备层（3 个）**：
- `blender_execute_operator` — 执行任意 bpy.ops.* 操作符
- `blender_execute_script` — 执行任意 Python 代码
- `blender_import_export` — 资产文件导入/导出

## Capabilities

### New Capabilities

- `perception-tools`: 11 个感知层工具，提供 LLM 对 Blender 状态的全方位读取能力
- `declarative-write-tools`: 3 个声明式写入工具，通过节点和时间轴接口完成复杂创作
- `imperative-write-tools`: 9 个命令式写入工具，覆盖对象/材质/修改器/UV/约束/物理等操作
- `fallback-tools`: 3 个后备工具，覆盖长尾需求
- `rich-input-schemas`: 为全部 26 个工具手写详细 JSON Schema，包含 enum、default、description 等
- `tool-annotations`: 为全部工具标注 MCP 工具注解（readOnly/destructive/idempotent/openWorld）
- `description-convention`: 三段式 description 模板（WHAT/WHEN/NOT）+ 交叉引用矩阵，降低 LLM 工具误选率
- `workflow-prompts`: 7 个 MCP Prompt 工作流模板（scene-setup/material-create/model-asset/animate/composite/render-output/diagnose），用户通过 /slash-command 触发，引导 LLM 组合使用工具

### Removed Capabilities

- `unified-data-crud`: 原 data.create/read/write/delete/list/link 6 个工具被拆分为更具体的工具
- `info-query`: 原 info.query 工具被拆分为多个感知层工具
- `opaque-payload-schema`: 移除 payload 包装层和无约束的 inputSchema

## Impact

- **代码影响**：
  - `src/blender_mcp/mcp_protocol.py` — 重写工具注册和调用路由，展平 payload
  - `src/blender_mcp/catalog/catalog.py` — 更新能力定义为 26 个新工具
  - `src/blender_mcp/schemas/` — 新建目录，存放每个工具的手写 JSON Schema
  - `src/blender_mcp_addon/capabilities/base.py` — 更新分发逻辑适配新工具名
  - `src/blender_mcp_addon/handlers/` — 现有 handler 保持不变，新增节点编辑/VSE/UV/约束/物理 handler

- **BREAKING 变更**：
  - 所有工具名从 `data.create` 格式变为 `blender_create_object` 格式
  - payload 包装层移除，参数直接暴露
  - 原有 8 个工具全部废弃，替换为 26 个新工具

- **新增 Handler**：
  - `handlers/nodes/` — 节点编辑 handler（覆盖 6 种节点上下文）
  - `handlers/sequencer/` — VSE 序列编辑 handler
  - `handlers/uv/` — UV 映射操作 handler
  - `handlers/constraints/` — 约束管理 handler
  - `handlers/physics/` — 物理模拟 handler

- **依赖**：无新增外部依赖
