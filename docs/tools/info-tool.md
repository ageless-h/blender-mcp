# 信息工具 (info.query) ⚠️ **已废弃**

> **注意**：此文档已废弃。`info.query` 工具已被拆分为多个感知层工具。请参阅：
> - [感知层工具 (Perception Layer)](./perception-layer.md)
>
> 具体映射：
> - `info.query(type="reports")` → 暂无直接映射，可通过 `blender_get_scene` 获取
> - `info.query(type="last_op")` → 暂无直接映射
> - `info.query(type="undo_history")` → 暂无直接映射
> - `info.query(type="scene_stats")` → `blender_get_scene`
> - `info.query(type="selection")` → `blender_get_selection`
> - `info.query(type="mode")` → `blender_get_selection`
> - `info.query(type="viewport_capture")` → `blender_capture_viewport`
> - `info.query(type="version")` → `blender_get_scene` (include=["version"])
> - `info.query(type="memory")` → `blender_get_scene` (include=["memory"])

---

信息工具负责查询 Blender 的状态、历史、反馈和统计信息。这对于 LLM 理解当前状态和验证操作结果至关重要。

## 工具签名

```python
info.query(
    type: InfoType,           # 查询类型
    params: dict = {}         # 查询参数（可选）
) -> dict
```

## 查询类型

| 类型 | 说明 |
|-----|------|
| `reports` | 最近的操作报告（信息/警告/错误） |
| `last_op` | 最后执行的操作及其结果 |
| `undo_history` | 撤销历史列表 |
| `scene_stats` | 场景统计信息 |
| `selection` | 当前选中状态 |
| `mode` | 当前编辑模式 |
| `changes` | 自上次查询以来的变化 |
| `depsgraph` | 依赖图更新信息 |
| `viewport_capture` | 视口截图 |
| `version` | Blender 版本信息 |
| `memory` | 内存使用情况 |

---

## 查询示例

### reports - 操作报告

获取最近的操作反馈信息，包括信息、警告和错误。

```python
info.query(type="reports", params={"limit": 10})
```

**返回值**：
```json
{
    "reports": [
        {"type": "INFO", "message": "Deleted 3 object(s)"},
        {"type": "WARNING", "message": "Some objects could not be deleted"},
        {"type": "ERROR", "message": "Operation cancelled"}
    ],
    "count": 3
}
```

### last_op - 最后操作

获取最后执行的操作及其详细结果。

```python
info.query(type="last_op")
```

**返回值**：
```json
{
    "operator": "mesh.subdivide",
    "success": true,
    "result": "FINISHED",
    "reports": [
        {"type": "INFO", "message": "Subdivided 6 face(s)"}
    ],
    "duration_ms": 12.5,
    "params": {
        "number_cuts": 2
    }
}
```

### undo_history - 撤销历史

获取操作历史列表。

```python
info.query(type="undo_history", params={"limit": 10})
```

**返回值**：
```json
{
    "current_step": 5,
    "total_steps": 12,
    "history": [
        {"index": 0, "name": "Original"},
        {"index": 1, "name": "Add Cube"},
        {"index": 2, "name": "Subdivide"},
        {"index": 3, "name": "Move"},
        {"index": 4, "name": "Scale"},
        {"index": 5, "name": "Add Material", "current": true}
    ],
    "can_undo": true,
    "can_redo": true
}
```

### scene_stats - 场景统计

获取当前场景的统计信息。

```python
info.query(type="scene_stats")
```

**返回值**：
```json
{
    "objects": 15,
    "objects_selected": 3,
    "vertices": 24680,
    "edges": 49152,
    "faces": 24576,
    "triangles": 49152,
    "memory_mb": 128.5,
    "active_object": "Cube",
    "scene_name": "Scene",
    "frame_current": 1,
    "frame_start": 1,
    "frame_end": 250,
    "render_engine": "CYCLES"
}
```

### selection - 选中状态

获取当前选中对象和元素的详细信息。

```python
info.query(type="selection")
```

**返回值**：
```json
{
    "mode": "EDIT",
    "active_object": "Cube",
    "selected_objects": ["Cube", "Sphere"],
    "edit_mesh": {
        "total_verts": 24,
        "total_edges": 48,
        "total_faces": 24,
        "selected_verts": 8,
        "selected_edges": 12,
        "selected_faces": 6
    }
}
```

对象模式下的返回值：
```json
{
    "mode": "OBJECT",
    "active_object": "Cube",
    "selected_objects": ["Cube", "Sphere", "Light"],
    "selected_count": 3
}
```

### mode - 编辑模式

获取当前编辑模式和相关信息。

```python
info.query(type="mode")
```

**返回值**：
```json
{
    "mode": "EDIT",
    "mode_string": "Edit Mode",
    "active_object": "Cube",
    "object_type": "MESH",
    "tool": "builtin.select_box",
    "workspace": "Modeling"
}
```

### changes - 变更追踪

获取自上次查询以来的场景变化。

```python
info.query(type="changes")
```

**返回值**：
```json
{
    "modified_objects": ["Cube", "Sphere"],
    "added_objects": ["Light.001"],
    "deleted_objects": ["Plane"],
    "geometry_updates": ["Cube"],
    "transform_updates": ["Cube", "Sphere"],
    "material_updates": ["Cube"],
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### depsgraph - 依赖图更新

获取依赖图更新信息，用于了解哪些数据被重新评估。

```python
info.query(type="depsgraph")
```

**返回值**：
```json
{
    "updates": [
        {
            "id_name": "Cube",
            "id_type": "OBJECT",
            "is_updated_geometry": true,
            "is_updated_transform": false
        },
        {
            "id_name": "Material",
            "id_type": "MATERIAL",
            "is_updated_shading": true
        }
    ]
}
```

### viewport_capture - 视口截图

捕获当前视口的截图。

```python
info.query(
    type="viewport_capture",
    params={
        "view": "current",        # current | camera | top | front | right
        "shading": "RENDERED",    # WIREFRAME | SOLID | MATERIAL | RENDERED
        "resolution": [1920, 1080],
        "format": "base64"        # base64 | filepath
    }
)
```

**返回值**：
```json
{
    "width": 1920,
    "height": 1080,
    "view": "current",
    "shading": "RENDERED",
    "format": "base64",
    "data": "iVBORw0KGgo..."
}
```

如果 `format` 为 `filepath`：
```json
{
    "width": 1920,
    "height": 1080,
    "view": "current",
    "shading": "RENDERED",
    "format": "filepath",
    "path": "/tmp/blender_mcp/viewport_capture_001.png"
}
```

### version - 版本信息

获取 Blender 版本和系统信息。

```python
info.query(type="version")
```

**返回值**：
```json
{
    "blender_version": [4, 0, 0],
    "blender_version_string": "4.0.0",
    "api_version": [4, 0, 0],
    "build_date": "2024-01-01",
    "build_platform": "Windows-10",
    "python_version": "3.11.6"
}
```

### memory - 内存使用

获取内存使用情况。

```python
info.query(type="memory")
```

**返回值**：
```json
{
    "total_mb": 8192.0,
    "used_mb": 512.5,
    "peak_mb": 768.0,
    "objects_mb": 128.0,
    "meshes_mb": 256.0,
    "images_mb": 64.0
}
```

---

## LLM 工作流示例

以下是 LLM 如何利用 info.query 进行智能操作的示例：

```python
# 1. 检查当前状态
state = info.query(type="selection")
if state["mode"] != "EDIT":
    data.write(type="context", properties={"mode": "EDIT"})

# 2. 执行操作
operator.execute("mesh.subdivide", {"number_cuts": 2})

# 3. 验证操作结果
result = info.query(type="last_op")
if not result["success"]:
    # 获取错误详情
    reports = info.query(type="reports")
    # 根据错误调整策略
    for report in reports["reports"]:
        if report["type"] == "ERROR":
            print(f"Error: {report['message']}")

# 4. 检查变更
changes = info.query(type="changes")
if "Cube" in changes["geometry_updates"]:
    print("Cube geometry was updated successfully")

# 5. 获取最终统计
stats = info.query(type="scene_stats")
print(f"Scene now has {stats['vertices']} vertices")

# 6. 获取视觉反馈
capture = info.query(
    type="viewport_capture",
    params={"shading": "RENDERED", "resolution": [512, 512]}
)
# LLM 可以分析图像验证结果
```

