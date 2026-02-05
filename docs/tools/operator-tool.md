# 操作工具 (operator.execute)

操作工具负责执行 Blender 操作符（`bpy.ops.*`），覆盖所有无法通过数据 CRUD 完成的操作。

## 工具签名

```python
operator.execute(
    operator: str,            # 操作符名称（如 "mesh.subdivide"）
    params: dict = {},        # 操作符参数
    context: dict = {}        # 上下文覆盖（可选）
) -> {
    "success": bool,
    "operator": str,
    "result": str,            # "FINISHED" | "CANCELLED" | ...
    "reports": list[dict],    # 操作报告
    "duration_ms": float
}
```

## 参数说明

### operator

操作符名称，格式为 `module.operator_name`，对应 `bpy.ops.module.operator_name`。

常用操作符模块：
- `object.*` - 对象操作
- `mesh.*` - 网格编辑
- `material.*` - 材质操作
- `node.*` - 节点操作
- `uv.*` - UV 操作
- `anim.*` - 动画操作
- `render.*` - 渲染操作
- `import_scene.*` / `export_scene.*` - 导入导出
- `sequencer.*` - 视频编辑

### params

操作符的参数，具体参数请参考 [Blender Operators 文档](https://docs.blender.org/api/current/bpy.ops.html)。

### context

上下文覆盖参数，用于在执行操作前设置正确的上下文环境。

| 参数 | 说明 |
|-----|------|
| `active_object` | 设置活动对象 |
| `selected_objects` | 设置选中对象列表 |
| `mode` | 设置编辑模式（OBJECT/EDIT/SCULPT/...） |
| `area_type` | 设置区域类型（VIEW_3D/NODE_EDITOR/...） |

---

## 使用示例

### 基础对象操作

```python
# 添加立方体
operator.execute("mesh.primitive_cube_add", {
    "size": 2.0,
    "location": [0, 0, 1]
})

# 删除选中对象
operator.execute("object.delete")

# 复制对象
operator.execute("object.duplicate", {"linked": False})

# 应用变换
operator.execute("object.transform_apply", {
    "location": True,
    "rotation": True,
    "scale": True
})
```

### 网格编辑

```python
# 细分（需要编辑模式）
operator.execute(
    "mesh.subdivide",
    {"number_cuts": 2},
    {"mode": "EDIT", "active_object": "Cube"}
)

# 挤出
operator.execute(
    "mesh.extrude_region_move",
    {"TRANSFORM_OT_translate": {"value": [0, 0, 1]}},
    {"mode": "EDIT"}
)

# 倒角
operator.execute(
    "mesh.bevel",
    {"offset": 0.1, "segments": 3},
    {"mode": "EDIT"}
)

# 合并顶点
operator.execute(
    "mesh.merge",
    {"type": "CENTER"},
    {"mode": "EDIT"}
)
```

### 修改器操作

```python
# 添加修改器
operator.execute("object.modifier_add", {"type": "SUBSURF"})
operator.execute("object.modifier_add", {"type": "MIRROR"})
operator.execute("object.modifier_add", {"type": "SOLIDIFY"})

# 应用修改器
operator.execute("object.modifier_apply", {"modifier": "Subdivision"})

# 移除修改器
operator.execute("object.modifier_remove", {"modifier": "Mirror"})
```

### UV 操作

```python
# UV 展开（需要编辑模式）
operator.execute(
    "uv.unwrap",
    {"method": "ANGLE_BASED", "margin": 0.02},
    {"mode": "EDIT", "active_object": "Cube"}
)

# 智能 UV 投影
operator.execute(
    "uv.smart_project",
    {"angle_limit": 66, "island_margin": 0.02},
    {"mode": "EDIT"}
)

# UV 打包
operator.execute("uv.pack_islands", {"margin": 0.02})
```

### 节点操作

```python
# 添加节点（需要节点编辑器上下文）
operator.execute(
    "node.add_node",
    {"type": "ShaderNodeMixRGB"},
    {"area_type": "NODE_EDITOR"}
)

# 连接节点
operator.execute("node.link", {...})

# 节点组
operator.execute("node.group_make")
```

### 动画操作

```python
# 插入关键帧
operator.execute("anim.keyframe_insert", {
    "type": "LocRotScale"
})

# 删除关键帧
operator.execute("anim.keyframe_delete", {
    "type": "Location"
})

# 播放动画
operator.execute("screen.animation_play")

# 跳转到帧
operator.execute("screen.frame_jump", {"end": False})
```

### 渲染操作

```python
# 渲染当前帧
operator.execute("render.render", {"write_still": True})

# 渲染动画
operator.execute("render.render", {"animation": True})

# 视口渲染（快速截图）
operator.execute("render.opengl", {"write_still": True})
```

### 导入导出

```python
# 导入 FBX
operator.execute("import_scene.fbx", {
    "filepath": "/path/to/model.fbx",
    "use_custom_normals": True
})

# 导入 OBJ
operator.execute("import_scene.obj", {
    "filepath": "/path/to/model.obj"
})

# 导出 GLTF
operator.execute("export_scene.gltf", {
    "filepath": "/path/to/output.glb",
    "export_format": "GLB"
})

# 导出 FBX
operator.execute("export_scene.fbx", {
    "filepath": "/path/to/output.fbx",
    "use_selection": True
})
```

### 文件操作

```python
# 保存文件
operator.execute("wm.save_mainfile")

# 另存为
operator.execute("wm.save_as_mainfile", {
    "filepath": "/path/to/file.blend"
})

# 追加资产
operator.execute("wm.append", {
    "filepath": "/path/to/library.blend/Object/Cube",
    "filename": "Cube",
    "directory": "/path/to/library.blend/Object/"
})

# 链接资产
operator.execute("wm.link", {
    "filepath": "/path/to/library.blend/Object/Cube",
    "filename": "Cube",
    "directory": "/path/to/library.blend/Object/"
})
```

### 视频编辑 (VSE)

```python
# 添加视频片段
operator.execute("sequencer.movie_strip_add", {
    "filepath": "/path/to/video.mp4",
    "frame_start": 1,
    "channel": 1
})

# 添加音频片段
operator.execute("sequencer.sound_strip_add", {
    "filepath": "/path/to/audio.mp3",
    "frame_start": 1,
    "channel": 2
})

# 剪切
operator.execute("sequencer.cut", {"frame": 100})

# 添加转场
operator.execute("sequencer.effect_strip_add", {"type": "CROSS"})
```

### 物理模拟

```python
# 烘焙物理缓存
operator.execute("ptcache.bake_all", {"bake": True})

# 清除缓存
operator.execute("ptcache.free_bake_all")

# 添加刚体
operator.execute("rigidbody.object_add", {"type": "ACTIVE"})

# 烘焙流体
operator.execute("fluid.bake_all")
```

---

## 上下文覆盖详解

许多操作符需要特定的上下文才能执行。`context` 参数允许在执行前临时设置上下文。

### 内部实现原理

```python
# Blender 3.2+ 使用 temp_override
with bpy.context.temp_override(
    active_object=obj,
    selected_objects=[obj],
    mode='EDIT'
):
    bpy.ops.mesh.subdivide(number_cuts=2)
```

### 常见上下文需求

| 操作类型 | 需要的上下文 |
|---------|------------|
| 网格编辑 (`mesh.*`) | `mode="EDIT"` |
| UV 编辑 (`uv.*`) | `mode="EDIT"`, `area_type="IMAGE_EDITOR"` |
| 雕刻 (`sculpt.*`) | `mode="SCULPT"` |
| 权重绘制 (`paint.weight_*`) | `mode="WEIGHT_PAINT"` |
| 节点编辑 (`node.*`) | `area_type="NODE_EDITOR"` |
| 姿态模式 (`pose.*`) | `mode="POSE"` |

---

## 错误处理

操作符执行可能失败，返回的 `result` 字段表示执行结果：

| 结果 | 说明 |
|-----|------|
| `FINISHED` | 成功完成 |
| `CANCELLED` | 被取消 |
| `RUNNING_MODAL` | 模态运行中（不适用于 MCP） |
| `PASS_THROUGH` | 传递给其他操作符 |

`reports` 字段包含详细的报告信息：

```python
{
    "success": False,
    "result": "CANCELLED",
    "reports": [
        {"type": "WARNING", "message": "No active object"},
        {"type": "ERROR", "message": "Cannot execute in this context"}
    ]
}
```

