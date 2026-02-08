# Tool Migration Guide

> 更新日期: 2026-02-08

## 概述

Blender MCP 经历了两次架构演进：

1. **旧架构** (scene.read / scene.write) — 已废弃
2. **中间架构** (data.*/operator.execute/info.query, 8 工具) — 已废弃, 向后兼容
3. **当前架构** (26 个 blender_* 工具, 四层分层) — **推荐**

所有旧工具名称通过 _LEGACY_TOOL_MAP 自动映射到新工具。

---

## 完整映射表

### scene.* (第一代)

| 旧能力 | 新工具 | 说明 |
|--------|--------|------|
| scene.read | blender_get_scene / blender_get_objects | 按需选择 |
| scene.write | blender_create_object / blender_modify_object | 按操作选择 |

### data.* (第二代)

| 旧工具 | 新工具 | 说明 |
|--------|--------|------|
| data_create | blender_create_object | 对象创建 |
| data_read | blender_get_object_data | 或其他 blender_get_* |
| data_write | blender_modify_object | 或 blender_manage_* |
| data_delete | blender_modify_object | delete: true |
| data_list | blender_get_objects | 或 blender_get_materials |
| data_link | blender_manage_collection | link/unlink |
| operator_execute | blender_execute_operator | 直接映射 |
| info_query | 见下表 | 拆分为多个感知层工具 |
| script_execute | blender_execute_script | 直接映射 |
### info.query 类型映射

| info.query 类型 | 新工具 | 参数 |
|----------------|--------|------|
| scene_stats | blender_get_scene | include: ["stats"] |
| selection | blender_get_selection | 无 |
| mode | blender_get_selection | 无 |
| viewport_capture | blender_capture_viewport | shading, camera_view, format |
| version | blender_get_scene | include: ["version"] |
| memory | blender_get_scene | include: ["memory"] |

---

## 迁移示例

### 读取场景

**旧:** `info.query(type="scene_stats")`
**新:** `blender_get_scene(include=["stats", "render", "timeline"])`

### 创建对象

**旧:** `data.create(type="object", name="Cube")`
**新:** `blender_create_object(name="Cube", object_type="MESH", primitive="cube")`

### 修改对象

**旧:** `data.write(type="object", name="Cube", properties={location: [1,2,3]})`
**新:** `blender_modify_object(name="Cube", location=[1, 2, 3])`

### 管理材质

**旧:** `data.create(type="material", name="Red")`
**新:** `blender_manage_material(action="create", name="Red", base_color=[1,0,0,1])`

---

## 新架构优势

| 对比项 | 旧架构 (data.*) | 新架构 (blender_*) |
|--------|-----------------|-------------------|
| 工具数量 | 8 | 26 |
| LLM 理解 | 需理解内部类型系统 | 意图驱动, Schema 自描述 |
| 参数格式 | 嵌套 payload | 展平, 无包装层 |
| 枚举约束 | 无 | 每个分类参数有 enum |
| 工具注解 | 无 | readOnly/destructive/idempotent |
| 覆盖率 | 99% | 99.9% (四层覆盖) |

---

## 废弃时间线

- **当前**: 旧名称可用, 自动映射到新工具
- **下一主版本**: 旧名称将被移除
