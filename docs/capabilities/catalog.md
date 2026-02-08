# Capability Catalog

> 更新日期: 2026-02-08 — 与 26 工具架构同步

## 架构概览

Blender MCP 采用四层分层架构，共 26 个工具：

| 层 | 工具数 | 说明 |
|----|--------|------|
| 感知层 (Perception) | 11 | 只读查询 Blender 状态 |
| 声明式写入层 (Declarative Write) | 3 | 节点/动画/VSE 批量编辑 |
| 命令式写入层 (Imperative Write) | 9 | 对象/材质/修改器等基础操作 |
| 后备层 (Fallback) | 3 | 操作符/脚本/导入导出 |

详细设计文档: [工具架构总览](../tools/overview.md)

---

## 感知层 (11 tools) — readOnly

| 工具 | 内部能力 | 说明 |
|------|----------|------|
| `blender_get_objects` | `blender.get_objects` | 列出/筛选场景对象 |
| `blender_get_object_data` | `blender.get_object_data` | 单对象深度数据（12 种 include） |
| `blender_get_node_tree` | `blender.get_node_tree` | 读取节点树（6 种上下文） |
| `blender_get_animation_data` | `blender.get_animation_data` | 关键帧/NLA/驱动器/形态键 |
| `blender_get_materials` | `blender.get_materials` | 材质资产列表 |
| `blender_get_scene` | `blender.get_scene` | 场景统计/渲染/世界/版本/内存 |
| `blender_get_collections` | `blender.get_collections` | 集合层级树 |
| `blender_get_armature_data` | `blender.get_armature_data` | 骨架/骨骼层级/约束/姿态 |
| `blender_get_images` | `blender.get_images` | 纹理/图片资产列表 |
| `blender_capture_viewport` | `blender.capture_viewport` | 视口截图 |
| `blender_get_selection` | `blender.get_selection` | 当前选择/模式/活动对象 |

## 声明式写入层 (3 tools)

| 工具 | 内部能力 | 说明 |
|------|----------|------|
| `blender_edit_nodes` | `blender.edit_nodes` | 编辑任意节点树（add/remove/connect/set_value） |
| `blender_edit_animation` | `blender.edit_animation` | 关键帧/NLA/驱动器/形态键/帧范围 |
| `blender_edit_sequencer` | `blender.edit_sequencer` | VSE 条带/转场/特效 |

## 命令式写入层 (9 tools)

| 工具 | 内部能力 | 说明 |
|------|----------|------|
| `blender_create_object` | `blender.create_object` | 创建对象（MESH/LIGHT/CAMERA/CURVE/EMPTY/ARMATURE/TEXT） |
| `blender_modify_object` | `blender.modify_object` | 变换/父子/可见性/重命名/删除 |
| `blender_manage_material` | `blender.manage_material` | 材质 CRUD + PBR 属性 + 赋予 |
| `blender_manage_modifier` | `blender.manage_modifier` | 修改器 add/configure/apply/remove/move |
| `blender_manage_collection` | `blender.manage_collection` | 集合 CRUD + 对象链接 + 可见性 |
| `blender_manage_uv` | `blender.manage_uv` | UV 展开/缝合线/打包/图层 |
| `blender_manage_constraints` | `blender.manage_constraints` | 对象/骨骼约束 add/configure/remove |
| `blender_manage_physics` | `blender.manage_physics` | 物理模拟 add/configure/bake |
| `blender_setup_scene` | `blender.setup_scene` | 渲染引擎/输出/世界/时间线 |

## 后备层 (3 tools)

| 工具 | 内部能力 | 说明 |
|------|----------|------|
| `blender_execute_operator` | `blender.execute_operator` | 执行任意 bpy.ops.* |
| `blender_execute_script` | `blender.execute_script` | 执行 Python 代码（⚠️ 默认禁用） |
| `blender_import_export` | `blender.import_export` | 导入/导出 FBX/OBJ/GLTF/GLB/USD/STL |

---

## 工具注解

每个工具都带有 MCP 注解：

| 注解 | 含义 |
|------|------|
| `readOnlyHint` | 不修改 Blender 状态 |
| `destructiveHint` | 可能删除数据或不可逆更改 |
| `idempotentHint` | 重复调用产生相同结果 |
| `openWorldHint` | 访问外部网络/文件系统 |

## Schema 设计原则

1. **展平参数** — 无 `payload` 包装层
2. **枚举约束** — 分类参数使用 `enum`
3. **描述性字段** — 每个参数都有 `description`
4. **additionalProperties: false** — 防止 LLM 发明参数
5. **blender_ 前缀** — 避免多 MCP 服务器命名冲突
