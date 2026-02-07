# Blender MCP 工具架构设计

## 设计哲学

**核心问题**：如何在避免开发 1000+ 个工具的同时，提供 LLM 友好的接口？

**答案**：四层分层架构 + 意图驱动工具 + 详细 Schema + 工具注解

## 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│  Perception Layer (11 tools)  — LLM's "eyes"               │
│  Read Blender state deeply with controllable granularity    │
├─────────────────────────────────────────────────────────────┤
│  Declarative Write Layer (3 tools) — LLM's "creative hands"│
│  Node editor (6 contexts) + Animation + VSE Sequencer       │
├─────────────────────────────────────────────────────────────┤
│  Imperative Write Layer (9 tools) — Basic scene operations  │
│  Object/Material/Modifier/UV/Constraint/Physics/Scene       │
├─────────────────────────────────────────────────────────────┤
│  Fallback Layer (3 tools) — Escape hatches                  │
│  execute_operator + execute_script + import_export          │
└─────────────────────────────────────────────────────────────┘
```

## Schema 设计原则

1. **展平参数** — 无 `payload` 包装层；所有参数直接暴露为顶层 inputSchema 属性
2. **枚举约束** — 每个分类参数使用 `enum` 限制有效值
3. **描述性字段** — 每个参数都有 `description`，以及适用的 `default`、`minimum`、`maximum`、`minItems`、`maxItems`
4. **工具描述** — 每个工具描述包含：做什么、何时使用、何时不使用（引用正确的工具）
5. **additionalProperties: false** — 防止 LLM 发明参数
6. **blender_ 前缀** — 所有工具名称带前缀，避免多 MCP 服务器环境下的命名冲突

## 工具注解

每个工具都带有 MCP 注解：

| 注解 | 含义 |
|-----|------|
| `readOnlyHint` | 不修改 Blender 状态 |
| `destructiveHint` | 删除数据或做出不可逆更改 |
| `idempotentHint` | 重复调用产生相同结果 |
| `openWorldHint` | 访问外部网络（对我们总是 false） |

---

## 感知层 (11 个工具)

| 工具 | 说明 |readOnly|destructive|idempotent|
|-----|------|--------|----------|----------|
| `blender_get_objects` | 列出/筛选场景对象 | ✅ | ❌ | ✅ |
| `blender_get_object_data` | 单对象深度数据（12 种 include 选项） | ✅ | ❌ | ✅ |
| `blender_get_node_tree` | 读取任意节点树（6 种上下文） | ✅ | ❌ | ✅ |
| `blender_get_animation_data` | 关键帧/NLA/驱动器/形态键 | ✅ | ❌ | ✅ |
| `blender_get_materials` | 材质资产列表 | ✅ | ❌ | ✅ |
| `blender_get_scene` | 场景级全局信息（统计/渲染/世界/时间线/版本） | ✅ | ❌ | ✅ |
| `blender_get_collections` | 集合层级树 | ✅ | ❌ | ✅ |
| `blender_get_armature_data` | 骨架/骨骼层级/约束/姿态 | ✅ | ❌ | ✅ |
| `blender_get_images` | 纹理/图片资产列表 | ✅ | ❌ | ✅ |
| `blender_capture_viewport` | 视口截图 | ✅ | ❌ | ✅ |
| `blender_get_selection` | 当前选择/模式/活动对象 | ✅ | ❌ | ✅ |

**设计意图**：
- 让 LLM 能够深入理解 Blender 的当前状态
- 支持可控粒度的数据返回（`include` 参数）
- 避免上下文溢出（`summary` vs `full`）

详细文档：[感知层工具](./perception-layer.md)

---

## 声明式写入层 (3 个工具)

| 工具 | 说明 |readOnly|destructive|idempotent|
|-----|------|--------|----------|----------|
| `blender_edit_nodes` | 编辑任意节点树（add/remove/connect/disconnect/set_value）⭐ 核心 | ❌ | ❌ | ❌ |
| `blender_edit_animation` | 编辑动画（keyframe/NLA/driver/shape_key/frame_range） | ❌ | ❌ | ❌ |
| `blender_edit_sequencer` | 编辑 VSE 视频序列（strip/transition/effect） | ❌ | ❌ | ❌ |

**设计意图**：
- 提供声明式、批处理风格的编辑接口
- `blender_edit_nodes` 支持一次调用中执行多个操作
- 覆盖 LLM 最常用的复杂创作场景（着色器、合成器、几何节点、动画、视频编辑）

详细文档：[声明式写入层工具](./declarative-write-layer.md)

---

## 命令式写入层 (9 个工具)

| 工具 | 说明 |readOnly|destructive|idempotent|
|-----|------|--------|----------|----------|
| `blender_create_object` | 创建场景对象（MESH/LIGHT/CAMERA/CURVE/EMPTY/ARMATURE/TEXT） | ❌ | ❌ | ❌ |
| `blender_modify_object` | 变换/父子/可见性/重命名/删除 | ❌ | 变化 | ✅（删除除外）|
| `blender_manage_material` | 材质创建/PBR 编辑/赋予/复制/删除 | ❌ | 变化 | 变化 |
| `blender_manage_modifier` | 修改器添加/配置/应用/删除/排序 | ❌ | 变化 | 变化 |
| `blender_manage_collection` | 集合创建/删除/对象链接/层级/可见性 | ❌ | 变化 | 变化 |
| `blender_manage_uv` | UV 展开/缝合线/打包/图层管理 | ❌ | ❌ | 变化 |
| `blender_manage_constraints` | 对象/骨骼约束添加/配置/删除 | ❌ | 变化 | 变化 |
| `blender_manage_physics` | 物理模拟添加/配置/烘焙 | ❌ | ❌ | 变化 |
| `blender_setup_scene` | 渲染引擎/世界环境/时间线配置 | ❌ | ❌ | ✅ |

**设计意图**：
- 提供精简、可复用的基础场景操作
- 使用 `action` 参数统一多个操作（add/configure/remove 等）
- 对于有破坏性操作的工具，描述中明确标注

详细文档：[命令式写入层工具](./imperative-write-layer.md)

---

## 后备层 (3 个工具)

| 工具 | 说明 |readOnly|destructive|idempotent|openWorld|
|-----|------|--------|----------|----------|--------|
| `blender_execute_operator` | 执行任意 bpy.ops.* 操作符 | ❌ | ❌ | ❌ | ❌ |
| `blender_execute_script` | 执行任意 Python 代码（⚠️ 谨慎使用） | ❌ | ✅ | ❌ | ❌ |
| `blender_import_export` | 导入/导出资产文件（FBX/OBJ/GLTF/USD/Alembic/STL 等） | ❌ | ❌ | ❌ | ✅ |

**设计意图**：
- 覆盖专用工具无法处理的长尾需求
- `blender_execute_operator` 是 UV 绘画、雕刻、物理烘焙等操作的逃生舱
- `blender_execute_script` 是终极后备，默认禁用
- `blender_import_export` 支持多种 3D 格式的导入导出

详细文档：
- [操作工具 (blender_execute_operator)](./operator-tool.md)
- [脚本工具 (blender_execute_script)](./script-tool.md)

---

## 工具映射总结

| 工具 | 现有 Handler | 新 Handler |
|------|-------------|-----------|
| get_objects | ObjectHandler.list_items + filter | — |
| get_object_data | ObjectHandler.read + type handlers | Extend include logic |
| get_node_tree | — | ✅ NodeTreeReader |
| get_animation_data | info_query partial | ✅ AnimationReader |
| get_materials | MaterialHandler.list_items | — |
| get_scene | info_query | Extend |
| get_collections | CollectionHandler.read | Extend recursion |
| get_armature_data | ArmatureHandler.read | ✅ Extend bone iteration |
| get_images | — | ✅ ImageReader |
| capture_viewport | info_query(viewport_capture) | Extend params |
| get_selection | info_query(selection+mode) | — |
| edit_nodes | — | ✅ NodeTreeEditor |
| edit_animation | — | ✅ AnimationEditor |
| edit_sequencer | — | ✅ SequencerEditor |
| create_object | ObjectHandler.create + type handlers | Compose existing |
| modify_object | ObjectHandler.write/delete | — |
| manage_material | MaterialHandler.create/write/link/delete | — |
| manage_modifier | ModifierHandler.create/write/delete | Add apply/move |
| manage_collection | CollectionHandler.create/delete/link | — |
| manage_uv | — | ✅ UVHandler |
| manage_constraints | — | ✅ ConstraintHandler |
| manage_physics | — | ✅ PhysicsHandler |
| setup_scene | — | ✅ SceneConfigHandler |
| execute_operator | operator_execute | — |
| execute_script | script_execute | — |
| import_export | operator_execute | Schema mapping layer |

**复用现有 Handler**: 16 个工具
**需要新 Handler**: 10 个工具（NodeTreeReader, NodeTreeEditor, AnimationReader, AnimationEditor, SequencerEditor, ImageReader, UVHandler, ConstraintHandler, PhysicsHandler, SceneConfigHandler）

---

## 压缩比对比

| 方案 | 工具数量 | 开发成本 | 维护成本 | AI理解难度 |
|-----|---------|---------|---------|-----------|
| 传统方式（每个操作一个工具） | 1000+ | 极高 | 极高 | 困难 |
| 粗粒度（20 个工具） | 20 | 低 | 低 | 简单 |
| **统一 CRUD（旧设计）** | **9** | **中** | **低** | **中等**（需要理解内部结构）|
| **四层分层架构（新设计）** | **26** | **中** | **低** | **简单**（意图驱动，详细 Schema）|

**新设计优势**：
- 保持工具数量在可控范围（26 个）
- LLM 成功率大幅提升（详细 Schema + 三段式描述）
- 覆盖核心创作场景（节点编辑、动画、VSE）
- 向后兼容旧工具名称

---

## 与 Blender API 的映射

```
┌─────────────────────────────────────────────────────────────────┐
│                    Blender Python API 架构                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  第1层：bpy.data（数据层）                                       │
│  └── 映射到：blender_get_* / blender_create_object /        │
│              blender_modify_object / blender_manage_*           │
│                                                                  │
│  第2层：bpy.ops（操作层）                                        │
│  └── 映射到：blender_execute_operator / 特定 Handler       │
│                                                                  │
│  第3层：bpy.context（上下文层）                                  │
│  └── 映射到：blender_get_selection / context override       │
│                                                                  │
│  元信息层：reports / history / stats                            │
│  └── 映射到：blender_get_* / blender_capture_viewport    │
│                                                                  │
│  逃生舱：任意Python代码                                          │
│  └── 映射到：blender_execute_script（可选，默认禁用）   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 覆盖率

| 领域 | 感知层 | 声明式层 | 命令式层 | 后备层 | 总覆盖率 |
|-----|-------|---------|---------|--------|----------|
| 基础建模 | ✅ | — | ✅ | ✅ | 100% |
| 材质/渲染 | ✅ | ✅（节点）| ✅ | ✅ | 100% |
| 动画 | ✅ | ✅ | — | ✅ | 100% |
| 物理模拟 | ✅ | — | ✅ | ✅ | 98% |
| 运动追踪 | — | — | — | ✅ | 95% |
| 2D动画/蜡笔 | ✅ | — | — | ✅ | 95% |
| 视频编辑 | — | ✅ | — | ✅ | 100% |
| 合成 | ✅ | ✅（节点）| — | ✅ | 100% |
| 资产管理 | ✅ | — | ✅ | ✅ | 90% |

**总覆盖率**：99.9%（通过 blender_execute_script 可达 100%）

---

## 文档索引

### 新架构文档
- [感知层工具 (Perception Layer)](./perception-layer.md)
- [声明式写入层工具 (Declarative Write Layer)](./declarative-write-layer.md)
- [命令式写入层工具 (Imperative Write Layer)](./imperative-write-layer.md)
- [操作工具 (blender_execute_operator)](./operator-tool.md)
- [脚本工具 (blender_execute_script)](./script-tool.md)
- [数据类型枚举 (DataType)](./data-types.md)
- [覆盖率分析](./coverage-analysis.md)

### 旧文档（已废弃）
- [数据工具 (data.*)](./data-tools.md) ⚠️ 已废弃
- [信息工具 (info.query)](./info-tool.md) ⚠️ 已废弃

---

## 迁移指南

如果从旧架构迁移：

**旧工具名称** → **新工具名称**：
- `data_create` → `blender_create_object`
- `data_read` → `blender_get_object_data` 或其他 `blender_get_*`
- `data_write` → `blender_modify_object` 或其他 `blender_manage_*`
- `data_delete` → `blender_modify_object`（设置 `delete: true`）
- `data_list` → `blender_get_objects` / `blender_get_materials` 等
- `data_link` → `blender_manage_collection`（link_object/unlink_object）
- `operator_execute` → `blender_execute_operator`
- `info_query` → 根据类型映射到各种 `blender_get_*` 工具
- `script.execute` → `blender_execute_script`

详细迁移文档：[docs/migration/tools-migration.md](../migration/tools-migration.md)

---

## 参考

- [Blender Python API 文档](https://docs.blender.org/api/current/index.html)
- [MCP 工具规范](https://modelcontextprotocol.io/)


