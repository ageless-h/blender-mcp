# 数据类型枚举 (DataType)

`DataType` 枚举定义了内部数据处理层支持的所有数据类型，映射到 Blender 的 `bpy.data.*` 集合。

> 注：外部 API 使用 26 个 `blender_*` 工具（如 `blender_create_object`、`blender_manage_modifier`）。
> 以下 DataType 是内部 handler 层的参考。

## 完整类型列表

```python
class DataType(str, Enum):
    # ═══════════════════════════════════════════════════════════
    # 核心对象类型
    # ═══════════════════════════════════════════════════════════
    OBJECT = "object"           # bpy.data.objects
    MESH = "mesh"               # bpy.data.meshes
    CURVE = "curve"             # bpy.data.curves
    SURFACE = "surface"         # bpy.data.curves (SURFACE type)
    METABALL = "metaball"       # bpy.data.metaballs
    ARMATURE = "armature"       # bpy.data.armatures
    LATTICE = "lattice"         # bpy.data.lattices
    
    # ═══════════════════════════════════════════════════════════
    # 外观/材质
    # ═══════════════════════════════════════════════════════════
    MATERIAL = "material"       # bpy.data.materials
    TEXTURE = "texture"         # bpy.data.textures
    IMAGE = "image"             # bpy.data.images
    WORLD = "world"             # bpy.data.worlds
    LINESTYLE = "linestyle"     # bpy.data.linestyles (Freestyle)
    
    # ═══════════════════════════════════════════════════════════
    # 灯光/相机
    # ═══════════════════════════════════════════════════════════
    CAMERA = "camera"           # bpy.data.cameras
    LIGHT = "light"             # bpy.data.lights
    PROBE = "probe"             # bpy.data.lightprobes
    
    # ═══════════════════════════════════════════════════════════
    # 节点系统
    # ═══════════════════════════════════════════════════════════
    NODE_TREE = "node_tree"     # bpy.data.node_groups
    # 节点树类型通过 params.type 指定：
    # - ShaderNodeTree (材质节点)
    # - GeometryNodeTree (几何节点)
    # - CompositorNodeTree (合成节点)
    # - TextureNodeTree (纹理节点)
    
    # ═══════════════════════════════════════════════════════════
    # 组织/场景
    # ═══════════════════════════════════════════════════════════
    COLLECTION = "collection"   # bpy.data.collections
    SCENE = "scene"             # bpy.data.scenes
    WORKSPACE = "workspace"     # bpy.data.workspaces
    
    # ═══════════════════════════════════════════════════════════
    # 动画
    # ═══════════════════════════════════════════════════════════
    ACTION = "action"           # bpy.data.actions
    
    # ═══════════════════════════════════════════════════════════
    # 2D/蜡笔
    # ═══════════════════════════════════════════════════════════
    GREASE_PENCIL = "grease_pencil"  # bpy.data.grease_pencils
    
    # ═══════════════════════════════════════════════════════════
    # 音视频
    # ═══════════════════════════════════════════════════════════
    SOUND = "sound"             # bpy.data.sounds
    SPEAKER = "speaker"         # bpy.data.speakers
    MOVIECLIP = "movieclip"     # bpy.data.movieclips
    MASK = "mask"               # bpy.data.masks
    
    # ═══════════════════════════════════════════════════════════
    # 物理/模拟
    # ═══════════════════════════════════════════════════════════
    PARTICLE = "particle"       # bpy.data.particles
    
    # ═══════════════════════════════════════════════════════════
    # 特殊几何
    # ═══════════════════════════════════════════════════════════
    VOLUME = "volume"           # bpy.data.volumes (OpenVDB)
    POINTCLOUD = "pointcloud"   # bpy.data.pointclouds
    HAIR_CURVES = "hair_curves" # bpy.data.hair_curves
    
    # ═══════════════════════════════════════════════════════════
    # 工具/资源
    # ═══════════════════════════════════════════════════════════
    BRUSH = "brush"             # bpy.data.brushes
    PALETTE = "palette"         # bpy.data.palettes
    PAINTCURVE = "paintcurve"   # bpy.data.paint_curves
    TEXT = "text"               # bpy.data.texts
    FONT = "font"               # bpy.data.fonts
    
    # ═══════════════════════════════════════════════════════════
    # 外部数据
    # ═══════════════════════════════════════════════════════════
    LIBRARY = "library"         # bpy.data.libraries
    CACHE_FILE = "cache_file"   # bpy.data.cache_files (Alembic/USD)
    
    # ═══════════════════════════════════════════════════════════
    # 伪类型（特殊处理）
    # ═══════════════════════════════════════════════════════════
    CONTEXT = "context"         # bpy.context (状态管理)
    PREFERENCES = "preferences" # bpy.context.preferences
    
    # ═══════════════════════════════════════════════════════════
    # 附属类型（需要父对象）
    # ═══════════════════════════════════════════════════════════
    MODIFIER = "modifier"       # object.modifiers
    CONSTRAINT = "constraint"   # object.constraints
    DRIVER = "driver"           # id.animation_data.drivers
    NLA_TRACK = "nla_track"     # object.animation_data.nla_tracks
```

## 类型分类

### 顶级数据块（Top-level ID）

这些类型存在于 `bpy.data.*` 中，是独立的数据块：

| 类型 | Blender 集合 | 说明 |
|-----|-------------|------|
| `object` | `bpy.data.objects` | 场景中的对象 |
| `mesh` | `bpy.data.meshes` | 网格数据 |
| `material` | `bpy.data.materials` | 材质 |
| `image` | `bpy.data.images` | 图像 |
| `node_tree` | `bpy.data.node_groups` | 节点组 |
| `collection` | `bpy.data.collections` | 集合 |
| `scene` | `bpy.data.scenes` | 场景 |
| ... | ... | ... |

### 附属类型（Sub-data）

这些类型附属于父对象，需要指定父对象才能访问：

| 类型 | 父对象 | 访问路径 |
|-----|-------|---------|
| `modifier` | object | `object.modifiers[name]` |
| `constraint` | object | `object.constraints[name]` |
| `driver` | any ID | `id.animation_data.drivers[index]` |
| `nla_track` | object | `object.animation_data.nla_tracks[name]` |

**附属类型操作示例**：

```python
# 添加修改器
blender_manage_modifier(
    action="add",
    object_name="Cube",
    modifier_name="Subdivision",
    modifier_type="SUBSURF"
)

# 修改修改器属性
blender_manage_modifier(
    action="configure",
    object_name="Cube",
    modifier_name="Subdivision",
    settings={"levels": 2, "render_levels": 3}
)

# 删除修改器
blender_manage_modifier(
    action="remove",
    object_name="Cube",
    modifier_name="Subdivision"
)
```

### 伪类型（Pseudo-types）

这些不是真正的数据块，但为了 API 一致性而作为类型处理：

| 类型 | 映射 | 说明 |
|-----|------|------|
| `context` | `bpy.context` | 当前上下文状态 |
| `preferences` | `bpy.context.preferences` | 用户偏好设置 |

## 类型详细说明

### object（对象）

场景中的对象，是 Blender 数据层次的核心。

```python
# 创建
blender_create_object(
    name="Cube",
    object_type="MESH",
    primitive="cube"
)

# 读取
blender_get_object_data(name="Cube")
# → {
#     "name": "Cube",
#     "type": "MESH",
#     "location": [0, 0, 0],
#     "rotation_euler": [0, 0, 0],
#     "scale": [1, 1, 1],
#     ...
# }

# 修改
blender_modify_object(
    name="Cube",
    location=[1, 2, 3],
    scale=[2, 2, 2]
)
```

### node_tree（节点树）

节点组，用于材质、几何节点、合成等。

```python
# 读取节点树
blender_get_node_tree(
    tree_type="GEOMETRY",
    context="MODIFIER",
    target="MyObject/GeometryNodes"
)

# 编辑节点树
blender_edit_nodes(
    tree_type="SHADER",
    context="OBJECT",
    target="MyMaterial",
    operations=[{"action": "add_node", "type": "ShaderNodeBsdfPrincipled", "name": "BSDF"}]
)
```

### context（上下文）

伪类型，用于读写当前上下文状态。

```python
# 读取当前选择状态
blender_get_selection()
# → {
#     "mode": "OBJECT",
#     "active_object": "Cube",
#     "selected_objects": ["Cube", "Sphere"]
# }

# 切换模式 / 修改上下文通过操作符
blender_execute_operator(
    operator="object.mode_set",
    params={"mode": "EDIT"}
)
```

## Blender API 映射表

| DataType | bpy.data 集合 | 创建方法 |
|----------|--------------|---------|
| `object` | `objects` | `objects.new(name, data)` |
| `mesh` | `meshes` | `meshes.new(name)` |
| `curve` | `curves` | `curves.new(name, type)` |
| `material` | `materials` | `materials.new(name)` |
| `image` | `images` | `images.new(name, w, h)` / `images.load(path)` |
| `node_tree` | `node_groups` | `node_groups.new(name, type)` |
| `collection` | `collections` | `collections.new(name)` |
| `scene` | `scenes` | `scenes.new(name)` |
| `camera` | `cameras` | `cameras.new(name)` |
| `light` | `lights` | `lights.new(name, type)` |
| `armature` | `armatures` | `armatures.new(name)` |
| `action` | `actions` | `actions.new(name)` |
| `world` | `worlds` | `worlds.new(name)` |
| `sound` | `sounds` | `sounds.load(path)` |
| `text` | `texts` | `texts.new(name)` |

