# 命令式写入层工具 (Imperative Write Layer)

命令式写入层提供 9 个工具，用于基础场景操作 — 对象创建与修改、材质管理、修改器、集合、UV、约束、物理和场景设置。

## 工具列表

| 工具 | readOnly | destructive | idempotent | 说明 |
|-----|---------|------------|------------|------|
| `blender_create_object` | ❌ | ❌ | ❌ | 创建场景对象（MESH/LIGHT/CAMERA/CURVE/EMPTY/ARMATURE/TEXT） |
| `blender_modify_object` | ❌ | 变化 | ✅（删除除外）| 变换/父子/可见性/重命名/删除 |
| `blender_manage_material` | ❌ | 变化 | 变化 | 材质创建/PBR 编辑/赋予/复制/删除 |
| `blender_manage_modifier` | ❌ | 变化 | 变化 | 修改器添加/配置/应用/删除/排序 |
| `blender_manage_collection` | ❌ | 变化 | 变化 | 集合创建/删除/对象链接/层级/可见性 |
| `blender_manage_uv` | ❌ | ❌ | 变化 | UV 展开/缝合线/打包/图层管理 |
| `blender_manage_constraints` | ❌ | 变化 | 变化 | 对象/骨骼约束添加/配置/删除 |
| `blender_manage_physics` | ❌ | ❌ | 变化 | 物理模拟添加/配置/烘焙 |
| `blender_setup_scene` | ❌ | ❌ | ✅ | 渲染引擎/世界环境/时间线配置 |

---

## blender_create_object

**用途**：创建新对象。支持网格原语、灯光、相机、曲线、空对象、骨架和文本对象。

**何时使用**：
- 创建新场景对象
- 添加灯光、相机等

**何时不使用**：
- 需要修改现有对象 → 使用 `blender_modify_object`
- 需要创建材质 → 使用 `blender_manage_material`

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `name` | string | ✅ | — | 新对象的名称。Blender 会在名称已存在时自动添加后缀 |
| `object_type` | string | 否 | `"MESH"` | 对象类型：`MESH`, `LIGHT`, `CAMERA`, `CURVE`, `EMPTY`, `ARMATURE`, `TEXT` |
| `primitive` | string | 否 | — | 网格原语形状。仅当 `object_type=MESH` 时使用：`cube`, `sphere`, `cylinder`, `cone`, `plane`, `torus`, `icosphere` |
| `size` | number | 否 | `2.0` | 网格原理的尺寸（Blender 单位）。最小值：0.001 |
| `segments` | integer | 否 | `32` | 球体/圆柱体/圆锥体/圆环的段数。最小值：3 |
| `light_type` | string | 否 | `"POINT"` | 灯光类型。仅当 `object_type=LIGHT` 时使用：`POINT`, `SUN`, `SPOT`, `AREA` |
| `energy` | number | 否 | `1000` | 灯光能量（瓦特）。仅用于 LIGHT 对象 |
| `color` | array | 否 | — | 灯光颜色 [r,g,b] 范围 0-1。仅用于 LIGHT 对象 |
| `lens` | number | 否 | `50` | 相机焦距（毫米）。仅用于 CAMERA 对象 |
| `clip_start` | number | 否 | `0.1` | 相机近裁剪距离。仅用于 CAMERA 对象 |
| `clip_end` | number | 否 | `1000` | 相机远裁剪距离。仅用于 CAMERA 对象 |
| `set_active_camera` | boolean | 否 | `false` | 将此相机设为活动场景相机。仅用于 CAMERA 对象 |
| `curve_type` | string | 否 | `"BEZIER"` | 样条类型。仅用于 CURVE 对象：`BEZIER`, `NURBS`, `POLY` |
| `body` | string | 否 | — | 文本内容。仅用于 TEXT 对象 |
| `extrude` | number | 否 | `0` | TEXT 对象的挤压深度 |
| `location` | array | 否 | `[0, 0, 0]` | 3D 位置 [x, y, z] |
| `rotation` | array | 否 | `[0, 0, 0]` | 欧拉旋转 [x, y, z]（弧度） |
| `scale` | array | 否 | `[1, 1, 1]` | 缩放 [x, y, z] |
| `collection` | string | 否 | — | 要链接到的集合。如省略则使用场景集合 |

**示例**：

```json
// 创建立方体
{
  "name": "Cube",
  "object_type": "MESH",
  "primitive": "cube",
  "size": 2.0,
  "location": [0, 0, 0]
}

// 创建点光源
{
  "name": "Light",
  "object_type": "LIGHT",
  "light_type": "POINT",
  "energy": 1000,
  "color": [1, 1, 1],
  "location": [5, 5, 5]
}

// 创建相机
{
  "name": "Camera",
  "object_type": "CAMERA",
  "lens": 35,
  "location": [0, -10, 5],
  "rotation": [1.57, 0, 0],
  "set_active_camera": true
}

// 创建文本
{
  "name": "Text",
  "object_type": "TEXT",
  "body": "Hello World",
  "extrude": 0.5
}
```

---

## blender_modify_object

**用途**：修改现有对象的属性 — 变换、父子关系、可见性、重命名、设置原点或删除。

**何时使用**：
- 移动、旋转、缩放对象
- 设置父子关系
- 删除对象

**何时不使用**：
- 需要管理修改器 → 使用 `blender_manage_modifier`
- 需要管理材质 → 使用 `blender_manage_material`
- 需要管理约束 → 使用 `blender_manage_constraints`

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `name` | string | ✅ | — | 要修改的对象名称 |
| `location` | array | 否 | — | 新的 3D 位置 [x, y, z] |
| `rotation` | array | 否 | — | 新的欧拉旋转 [x, y, z]（弧度） |
| `scale` | array | 否 | — | 新的缩放 [x, y, z] |
| `parent` | string | 否 | — | 父对象名称。设为 `''` 清除父对象 |
| `visible` | boolean | 否 | — | 视口可见性 |
| `hide_render` | boolean | 否 | — | 在渲染中隐藏 |
| `new_name` | string | 否 | — | 重命名对象 |
| `active` | boolean | 否 | — | 设为活动对象 |
| `selected` | boolean | 否 | — | 设置选择状态 |
| `origin` | string | 否 | — | 将原点设为几何中心、3D 光标或中点：`GEOMETRY`, `CURSOR`, `MEDIAN` |
| `delete` | boolean | 否 | `false` | 如果为 true，从场景中删除此对象 |
| `delete_data` | boolean | 否 | `true` | 删除时同时删除底层的数据块（网格、曲线等） |

**示例**：

```json
// 移动对象
{
  "name": "Cube",
  "location": [1, 2, 3]
}

// 旋转对象
{
  "name": "Cube",
  "rotation": [0, 0.785, 0]
}

// 设置父对象
{
  "name": "Cube",
  "parent": "Empty"
}

// 清除父对象
{
  "name": "Cube",
  "parent": ""
}

// 重命名对象
{
  "name": "Cube",
  "new_name": "MyCube"
}

// 设置为活动对象
{
  "name": "Cube",
  "active": true
}

// 删除对象
{
  "name": "Cube",
  "delete": true,
  "delete_data": true
}

// 设置原点到几何中心
{
  "name": "Cube",
  "origin": "GEOMETRY"
}
```

---

## blender_manage_material

**用途**：创建、编辑、赋予、复制或删除材质。仅用于高级别 PBR 属性编辑。

**何时使用**：
- 创建新材质
- 编辑基础 PBR 属性
- 将材质赋予对象

**何时不使用**：
- 需要节点级着色器编辑 → 使用 `blender_edit_nodes`（tree_type=SHADER）

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `action` | string | ✅ | — | 材质操作：`create`, `edit`, `assign`, `unassign`, `duplicate`, `delete` |
| `name` | string | ✅ | — | 材质名称。create: 期望的名称；edit/assign/duplicate/delete: 现有材质名称 |
| `base_color` | array | 否 | — | 基础颜色 [r,g,b,a] 范围 0-1。用于 create/edit |
| `metallic` | number | 否 | — | 金属度值 0-1。用于 create/edit |
| `roughness` | number | 否 | — | 粗糙度值 0-1。用于 create/edit |
| `specular` | number | 否 | — | 镜面值 0-1。用于 create/edit |
| `alpha` | number | 否 | — | Alpha 值 0-1。用于 create/edit |
| `emission_color` | array | 否 | — | 发光颜色 [r,g,b,a]。用于 create/edit |
| `emission_strength` | number | 否 | — | 发光强度。用于 create/edit |
| `use_fake_user` | boolean | 否 | — | 如果为 true，材质不会在未使用时自动删除 |
| `object_name` | string | 否 | — | assign/unassign 操作的对象名称 |
| `slot` | integer | 否 | — | assign/unassign 的材质槽索引（0-based） |

**示例**：

```json
// 创建材质
{
  "action": "create",
  "name": "RedMaterial",
  "base_color": [1, 0, 0, 1],
  "metallic": 0,
  "roughness": 0.5
}

// 编辑材质
{
  "action": "edit",
  "name": "RedMaterial",
  "base_color": [0.8, 0.2, 0.2, 1],
  "roughness": 0.3
}

// 赋予材质
{
  "action": "assign",
  "name": "RedMaterial",
  "object_name": "Cube",
  "slot": 0
}

// 取消赋予材质
{
  "action": "unassign",
  "name": "RedMaterial",
  "object_name": "Cube",
  "slot": 0
}

// 复制材质
{
  "action": "duplicate",
  "name": "RedMaterial"
}

// 删除材质
{
  "action": "delete",
  "name": "OldMaterial"
}
```

---

## blender_manage_modifier

**用途**：添加、配置、应用、删除或重新排序对象的修改器。

**何时使用**：
- 添加修改器
- 配置修改器参数
- 应用或删除修改器

**何时不使用**：
- 需要读取修改器详情 → 使用 `blender_get_object_data`（include=["modifiers"]）

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `action` | string | ✅ | — | 修改器操作：`add`, `configure`, `apply`, `remove`, `move_up`, `move_down` |
| `object_name` | string | ✅ | — | 对象名称 |
| `modifier_name` | string | 否 | — | 修改器名称。add: 期望的名称；configure/apply/remove/move: 现有名称 |
| `modifier_type` | string | 否 | — | 修改器类型。仅用于 add 操作：`SUBSURF`, `MIRROR`, `ARRAY`, `BOOLEAN`, `SOLIDIFY`, `BEVEL`, `SHRINKWRAP`, `DECIMATE`, `REMESH`, `WEIGHTED_NORMAL`, `SIMPLE_DEFORM`, `SKIN`, `WIREFRAME`, `SCREW`, `DISPLACE`, `CAST`, `SMOOTH`, `LAPLACIANSMOOTH`, `CORRECTIVE_SMOOTH`, `CURVE`, `LATTICE`, `WARP`, `WAVE`, `CLOTH`, `COLLISION`, `ARMATURE`, `MESH_DEFORM`, `HOOK`, `SURFACE_DEFORM`, `DATA_TRANSFER`, `NORMAL_EDIT`, `UV_PROJECT`, `UV_WARP`, `VERTEX_WEIGHT_EDIT`, `VERTEX_WEIGHT_MIX`, `VERTEX_WEIGHT_PROXIMITY`, `NODES` |
| `settings` | object | 否 | — | 修改器设置为键值对（如 `{"levels": 3, "render_levels": 4}` 用于 SUBSURF） |

**示例**：

```json
// 添加细分修改器
{
  "action": "add",
  "object_name": "Cube",
  "modifier_name": "Subdivision",
  "modifier_type": "SUBSURF",
  "settings": {
    "levels": 2,
    "render_levels": 4
  }
}

// 添加镜像修改器
{
  "action": "add",
  "object_name": "Cube",
  "modifier_name": "Mirror",
  "modifier_type": "MIRROR"
}

// 配置修改器
{
  "action": "configure",
  "object_name": "Cube",
  "modifier_name": "Subdivision",
  "settings": {
    "levels": 3
  }
}

// 应用修改器
{
  "action": "apply",
  "object_name": "Cube",
  "modifier_name": "Subdivision"
}

// 删除修改器
{
  "action": "remove",
  "object_name": "Cube",
  "modifier_name": "Mirror"
}

// 向上移动修改器
{
  "action": "move_up",
  "object_name": "Cube",
  "modifier_name": "Subdivision"
}
```

---

## blender_manage_collection

**用途**：创建、删除或管理集合 — 链接/取消链接对象、设置父集合、控制可见性、设置颜色标签。

**何时使用**：
- 组织场景对象到集合
- 管理集合层级

**何时不使用**：
- 需要读取集合数据 → 使用 `blender_get_collections`

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `action` | string | ✅ | — | 集合操作：`create`, `delete`, `link_object`, `unlink_object`, `set_visibility`, `set_parent` |
| `collection_name` | string | ✅ | — | 集合名称 |
| `object_name` | string | 否 | — | link/unlink 操作的对象名称 |
| `parent` | string | 否 | — | 父集合名称。create: 嵌套位置；set_parent: 新父集合 |
| `hide_viewport` | boolean | 否 | — | 隐藏集合在视口中（用于 set_visibility） |
| `hide_render` | boolean | 否 | — | 隐藏集合在渲染中（用于 set_visibility） |
| `color_tag` | string | 否 | — | 颜色标签用于视觉组织：`NONE`, `COLOR_01` 到 `COLOR_08` |

**示例**：

```json
// 创建集合
{
  "action": "create",
  "collection_name": "Props",
  "parent": "Scene Collection"
}

// 删除集合
{
  "action": "delete",
  "collection_name": "OldCollection"
}

// 链接对象到集合
{
  "action": "link_object",
  "collection_name": "Props",
  "object_name": "Cube"
}

// 取消链接对象
{
  "action": "unlink_object",
  "collection_name": "Props",
  "object_name": "Cube"
}

// 设置集合可见性
{
  "action": "set_visibility",
  "collection_name": "Props",
  "hide_viewport": false,
  "hide_render": false
}

// 设置颜色标签
{
  "action": "set_visibility",
  "collection_name": "Props",
  "color_tag": "COLOR_03"
}
```

---

## blender_manage_uv

**用途**：UV 映射操作 — 标记/清除缝合线、使用各种算法展开、打包/缩放 UV 岛、管理 UV 图层。

**何时使用**：
- 展开 UV
- 添加/删除 UV 图层
- 管理 UV 岛

**何时不使用**：
- 需要 UV 绘画（空间笔刷操作） → 使用 `blender_execute_operator`

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `action` | string | ✅ | — | UV 操作：`mark_seam`, `clear_seam`, `unwrap`, `smart_project`, `cube_project`, `cylinder_project`, `sphere_project`, `lightmap_pack`, `pack_islands`, `average_island_scale`, `add_uv_map`, `remove_uv_map`, `set_active_uv` |
| `object_name` | string | ✅ | — | 网格对象名称 |
| `uv_map_name` | string | 否 | — | UV 图层名称用于 add/remove/set_active 操作 |
| `angle_limit` | number | 否 | `66.0` | smart_project 的角度限制（度）。范围：0-89 |
| `island_margin` | number | 否 | `0.02` | pack_islands 和 smart_project 的岛边距。范围：0-1 |
| `correct_aspect` | boolean | 否 | `true` | 在 UV 投影中修正非方形纹理 |
| `selection_mode` | string | 否 | — | mark_seam 的自动选择边缘。`SHARP_EDGES` 使用自动平滑角度，`ANGLE_BASED` 使用 angle_limit |

**示例**：

```json
// 标记缝合线
{
  "action": "mark_seam",
  "object_name": "Cube",
  "selection_mode": "SHARP_EDGES"
}

// 清除缝合线
{
  "action": "clear_seam",
  "object_name": "Cube",
  "selection_mode": "SHARP_EDGES"
}

// 展开 UV
{
  "action": "unwrap",
  "object_name": "Cube"
}

// 智能投影
{
  "action": "smart_project",
  "object_name": "Cube",
  "angle_limit": 66.0,
  "island_margin": 0.02
}

// 打包 UV 岛
{
  "action": "pack_islands",
  "object_name": "Cube",
  "island_margin": 0.02
}

// 添加 UV 图层
{
  "action": "add_uv_map",
  "object_name": "Cube",
  "uv_map_name": "UV_Second"
}
```

---

## blender_manage_constraints

**用途**：在对象或骨骼上添加、配置、删除、启用/禁用或重新排序约束。

**何时使用**：
- 添加对象或骨骼约束
- 配置约束参数

**何时不使用**：
- 需要读取约束数据 → 使用 `blender_get_object_data`（include=["constraints"]）或 `blender_get_armature_data`（include=["constraints"]）

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `action` | string | ✅ | — | 约束操作：`add`, `configure`, `remove`, `enable`, `disable`, `move_up`, `move_down` |
| `target_type` | string | 否 | `"OBJECT"` | 约束是在对象还是骨骼上：`OBJECT`, `BONE` |
| `target_name` | string | ✅ | — | OBJECT 约束的对象名称；BONE 约束格式为 `'ArmatureName/BoneName'` |
| `constraint_name` | string | 否 | — | 约束名称。add: 期望的名称；configure/remove/enable/disable: 现有名称 |
| `constraint_type` | string | 否 | — | add 操作的约束类型：`COPY_LOCATION`, `COPY_ROTATION`, `COPY_SCALE`, `COPY_TRANSFORMS`, `LIMIT_DISTANCE`, `LIMIT_LOCATION`, `LIMIT_ROTATION`, `LIMIT_SCALE`, `TRACK_TO`, `DAMPED_TRACK`, `LOCKED_TRACK`, `IK`, `STRETCH_TO`, `FLOOR`, `CHILD_OF`, `FOLLOW_PATH`, `CLAMP_TO`, `PIVOT`, `MAINTAIN_VOLUME`, `TRANSFORMATION`, `SHRINKWRAP`, `ACTION` |
| `settings` | object | 否 | — | 约束设置为键值对（如 `{"target": "Empty", "influence": 0.5, "track_axis": "TRACK_NEGATIVE_Z"}`） |

**示例**：

```json
// 添加复制位置约束
{
  "action": "add",
  "target_type": "OBJECT",
  "target_name": "Cube",
  "constraint_name": "CopyLocation",
  "constraint_type": "COPY_LOCATION",
  "settings": {
    "target": "Empty",
    "influence": 0.5
  }
}

// 添加跟踪约束
{
  "action": "add",
  "target_type": "OBJECT",
  "target_name": "Camera",
  "constraint_name": "TrackTo",
  "constraint_type": "TRACK_TO",
  "settings": {
    "target": "Target"
  }
}

// 添加骨骼约束
{
  "action": "add",
  "target_type": "BONE",
  "target_name": "Armature/Bone_L",
  "constraint_name": "IK",
  "constraint_type": "IK"
}

// 禁用约束
{
  "action": "disable",
  "target_type": "OBJECT",
  "target_name": "Cube",
  "constraint_name": "CopyLocation"
}
```

---

## blender_manage_physics

**用途**：添加、配置、删除或烘焙对象的物理模拟 — 刚体、布料、软体、流体、粒子和力场。

**何时使用**：
- 添加物理模拟
- 配置物理参数
- 烘焙物理缓存

**何时不使用**：
- 需要读取物理数据 → 使用 `blender_get_object_data`（include=["physics"]）

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `action` | string | ✅ | — | 物理操作：`add`, `configure`, `remove`, `bake`, `free_bake` |
| `object_name` | string | ✅ | — | 对象名称 |
| `physics_type` | string | 否 | — | add 操作的物理类型：`RIGID_BODY`, `RIGID_BODY_PASSIVE`, `CLOTH`, `SOFT_BODY`, `FLUID_DOMAIN`, `FLUID_FLOW`, `PARTICLE`, `FORCE_FIELD` |
| `force_field_type` | string | 否 | — | 力场类型。仅用于 physics_type=FORCE_FIELD：`WIND`, `TURBULENCE`, `VORTEX`, `MAGNETIC`, `HARMONIC`, `CHARGE`, `DRAG`, `FORCE` |
| `settings` | object | 否 | — | 物理设置为键值对（如 `{"mass": 5, "friction": 0.5}` 用于 RIGID_BODY，`{"count": 5000, "lifetime": 50}` 用于 PARTICLE） |
| `frame_start` | integer | 否 | — | 烘焙开始帧 |
| `frame_end` | integer | 否 | — | 烘焙结束帧 |

**示例**：

```json
// 添加刚体
{
  "action": "add",
  "object_name": "Cube",
  "physics_type": "RIGID_BODY",
  "settings": {
    "mass": 5,
    "friction": 0.5
  }
}

// 添加布料
{
  "action": "add",
  "object_name": "Plane",
  "physics_type": "CLOTH",
  "settings": {
    "quality": 15
  }
}

// 添加粒子系统
{
  "action": "add",
  "object_name": "Cube",
  "physics_type": "PARTICLE",
  "settings": {
    "count": 5000,
    "lifetime": 50
  }
}

// 烘焙物理缓存
{
  "action": "bake",
  "object_name": "Cube",
  "frame_start": 1,
  "frame_end": 250
}

// 清除烘焙
{
  "action": "free_bake",
  "object_name": "Cube"
}
```

---

## blender_setup_scene

**用途**：配置场景级设置 — 渲染引擎和质量、输出分辨率和格式、世界环境基础、时间轴/FPS。

**何时使用**：
- 设置渲染引擎
- 配置输出设置
- 设置时间轴参数

**何时不使用**：
- 需要详细的世界着色器编辑 → 使用 `blender_edit_nodes`（tree_type=SHADER, context=WORLD）

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `engine` | string | 否 | — | 渲染引擎：`BLENDER_EEVEE`, `BLENDER_EEVEE_NEXT`, `CYCLES` |
| `samples` | integer | 否 | — | 渲染采样数。最小值：1 |
| `resolution_x` | integer | 否 | — | 输出宽度（像素）。最小值：1 |
| `resolution_y` | integer | 否 | — | 输出高度（像素）。最小值：1 |
| `output_format` | string | 否 | — | 输出文件格式：`PNG`, `JPEG`, `OPEN_EXR`, `TIFF`, `BMP`, `FFMPEG` |
| `output_path` | string | 否 | — | 输出文件/目录路径 |
| `film_transparent` | boolean | 否 | — | 使用透明背景渲染 |
| `denoising` | boolean | 否 | — | 启用渲染降噪 |
| `denoiser` | string | 否 | — | 降噪器类型（需要 denoising=true）：`OPTIX`, `OPENIMAGEDENOISE` |
| `background_color` | array | 否 | — | 世界背景颜色 [r,g,b,a] |
| `background_strength` | number | 否 | — | 世界背景强度 |
| `fps` | number | 否 | — | 每秒帧数 |
| `frame_start` | integer | 否 | — | 场景开始帧 |
| `frame_end` | integer | 否 | — | 场景结束帧 |
| `frame_current` | integer | 否 | — | 设置当前帧 |

**示例**：

```json
// 设置 Cycles 渲染
{
  "engine": "CYCLES",
  "samples": 128,
  "denoising": true,
  "denoiser": "OPTIX"
}

// 设置输出分辨率
{
  "resolution_x": 1920,
  "resolution_y": 1080,
  "output_format": "PNG",
  "output_path": "/renders/"
}

// 设置背景颜色
{
  "background_color": [0.1, 0.1, 0.1, 1],
  "background_strength": 1
}

// 设置时间轴
{
  "fps": 24,
  "frame_start": 1,
  "frame_end": 250,
  "frame_current": 1
}

// 设置透明背景
{
  "film_transparent": true
}
```
