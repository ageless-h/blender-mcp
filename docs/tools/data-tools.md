# 数据工具 (data.*) ⚠️ **已废弃**

> **注意**：此文档已废弃。请参阅新的四层架构文档：
> - [感知层工具 (Perception Layer)](./perception-layer.md)
> - [声明式写入层工具 (Declarative Write Layer)](./declarative-write-layer.md)
> - [命令式写入层工具 (Imperative Write Layer)](./imperative-write-layer.md)

---

数据层工具负责对 Blender 数据块（`bpy.data.*`）进行 CRUD 操作。

## 工具列表

| 工具 | 说明 | 对应 Blender API |
|-----|------|-----------------|
| `data.create` | 创建数据块 | `bpy.data.*.new()` |
| `data.read` | 读取数据块属性 | `bpy.data.*[name].*` |
| `data.write` | 修改数据块属性 | `bpy.data.*[name].* = value` |
| `data.delete` | 删除数据块 | `bpy.data.*.remove()` |
| `data.list` | 列出指定类型的所有数据块 | `list(bpy.data.*)` |
| `data.link` | 关联/取消关联数据块 | `collection.objects.link()` 等 |

---

## data.create

创建新的数据块。

### 签名

```python
data.create(
    type: DataType,           # 数据类型
    name: str,                # 名称
    params: dict = {}         # 创建参数
) -> {
    "name": str,              # 实际创建的名称（可能有后缀）
    "type": str,              # 数据类型
    "success": bool
}
```

### 示例

```python
# 创建网格对象
data.create(
    type="object",
    name="Cube",
    params={"mesh_name": "CubeMesh"}
)

# 创建材质
data.create(
    type="material",
    name="RedMaterial",
    params={"use_nodes": True}
)

# 创建几何节点组
data.create(
    type="node_tree",
    name="MyGeoNodes",
    params={"type": "GeometryNodeTree"}
)

# 创建集合
data.create(
    type="collection",
    name="MyCollection"
)
```

---

## data.read

读取数据块的属性。

### 签名

```python
data.read(
    type: DataType,           # 数据类型
    name: str = None,         # 名称（可选，不提供则返回概览）
    path: str = None,         # 属性路径（可选）
    params: dict = {}         # 额外参数
) -> dict
```

### 参数说明

| 参数 | 说明 |
|-----|------|
| `params.format` | 图像返回格式：`"base64"` / `"filepath"` |
| `params.evaluated` | 是否返回评估后的数据（应用修改器后） |
| `params.include_*` | 控制返回哪些数据字段 |

### 示例

```python
# 读取对象属性
data.read(type="object", name="Cube")
# → {"name": "Cube", "location": [0,0,0], "rotation_euler": [0,0,0], ...}

# 读取特定属性路径
data.read(type="object", name="Cube", path="location")
# → {"location": [0, 0, 0]}

# 读取嵌套属性
data.read(type="material", name="Material", path="node_tree.nodes")
# → {"nodes": ["Principled BSDF", "Material Output"]}

# 读取图像为 base64
data.read(
    type="image",
    name="Render Result",
    params={"format": "base64", "resolution": [512, 512]}
)
# → {"data": "iVBORw0KGgo...", "width": 512, "height": 512}

# 读取评估后的网格数据（应用修改器）
data.read(
    type="mesh",
    name="Cube",
    params={"evaluated": True}
)

# 读取上下文状态
data.read(type="context")
# → {"mode": "OBJECT", "active_object": "Cube", "selected_objects": [...]}
```

---

## data.write

修改数据块的属性。

### 签名

```python
data.write(
    type: DataType,           # 数据类型
    name: str,                # 名称
    properties: dict          # 要修改的属性
) -> {
    "success": bool,
    "modified": list[str]     # 被修改的属性列表
}
```

### 示例

```python
# 修改对象位置
data.write(
    type="object",
    name="Cube",
    properties={"location": [1, 2, 3]}
)

# 修改多个属性
data.write(
    type="object",
    name="Cube",
    properties={
        "location": [1, 2, 3],
        "rotation_euler": [0, 0, 0.785],  # 45度
        "scale": [2, 2, 2]
    }
)

# 修改嵌套属性（材质节点）
data.write(
    type="material",
    name="Material",
    properties={
        "node_tree.nodes.Principled BSDF.inputs.Base Color.default_value": [1, 0, 0, 1]
    }
)

# 切换编辑模式
data.write(
    type="context",
    properties={"mode": "EDIT"}
)

# 切换工作区
data.write(
    type="context",
    properties={"workspace": "Shading"}
)

# 设置活动对象
data.write(
    type="context",
    properties={
        "active_object": "Cube",
        "selected_objects": ["Cube", "Sphere"]
    }
)
```

---

## data.delete

删除数据块。

### 签名

```python
data.delete(
    type: DataType,           # 数据类型
    name: str                 # 名称
) -> {
    "success": bool,
    "deleted": str
}
```

### 示例

```python
# 删除对象
data.delete(type="object", name="Cube")

# 删除材质
data.delete(type="material", name="Material.001")

# 删除集合
data.delete(type="collection", name="OldCollection")
```

---

## data.list

列出指定类型的所有数据块。

### 签名

```python
data.list(
    type: DataType,           # 数据类型
    filter: dict = {}         # 过滤条件（可选）
) -> {
    "type": str,
    "count": int,
    "items": list[dict]       # 数据块列表
}
```

### 示例

```python
# 列出所有对象
data.list(type="object")
# → {"type": "object", "count": 5, "items": [{"name": "Cube"}, {"name": "Light"}, ...]}

# 列出所有材质
data.list(type="material")

# 列出所有网格类型对象
data.list(type="object", filter={"object_type": "MESH"})

# 列出所有几何节点组
data.list(type="node_tree", filter={"tree_type": "GeometryNodeTree"})
```

---

## data.link

关联或取消关联数据块之间的关系。

### 签名

```python
data.link(
    source: dict,             # 源数据块 {"type": ..., "name": ...}
    target: dict,             # 目标数据块 {"type": ..., "name": ...}
    unlink: bool = False      # True 表示取消关联
) -> {
    "success": bool,
    "action": "link" | "unlink"
}
```

### 示例

```python
# 将对象添加到集合
data.link(
    source={"type": "object", "name": "Cube"},
    target={"type": "collection", "name": "MyCollection"}
)

# 从集合中移除对象
data.link(
    source={"type": "object", "name": "Cube"},
    target={"type": "collection", "name": "MyCollection"},
    unlink=True
)

# 将材质关联到对象
data.link(
    source={"type": "material", "name": "RedMaterial"},
    target={"type": "object", "name": "Cube"}
)

# 将几何节点组关联到修改器
data.link(
    source={"type": "node_tree", "name": "MyGeoNodes"},
    target={"type": "modifier", "object": "Cube", "name": "GeometryNodes"}
)
```

---

## 特殊类型处理

### context 伪类型

`context` 不是真正的数据块，而是 `bpy.context` 的状态管理。

```python
# 读取上下文
data.read(type="context")
# → {
#     "mode": "OBJECT",
#     "active_object": "Cube",
#     "selected_objects": ["Cube", "Sphere"],
#     "scene": "Scene",
#     "workspace": "Layout"
# }

# 修改上下文
data.write(type="context", properties={
    "mode": "EDIT",
    "active_object": "Cube"
})
```

### preferences 伪类型

`preferences` 映射到 `bpy.context.preferences`。

```python
# 读取偏好设置
data.read(type="preferences", path="view.show_tooltips")

# 修改偏好设置
data.write(type="preferences", properties={
    "view.show_tooltips": True
})
```

