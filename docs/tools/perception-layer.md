# 感知层工具 (Perception Layer)

感知层提供 11 个只读工具，让 LLM 深入理解 Blender 的当前状态。所有工具都是只读、非破坏性的，且幂等的。

## 工具列表

| 工具 | readOnly | destructive | idempotent | 说明 |
|-----|---------|------------|------------|------|
| `blender_get_objects` | ✅ | ❌ | ✅ | 列出/筛选场景对象 |
| `blender_get_object_data` | ✅ | ❌ | ✅ | 单对象深度数据（12 种 include 选项） |
| `blender_get_node_tree` | ✅ | ❌ | ✅ | 读取任意节点树（6 种上下文） |
| `blender_get_animation_data` | ✅ | ❌ | ✅ | 关键帧/NLA/驱动器/形态键 |
| `blender_get_materials` | ✅ | ❌ | ✅ | 材质资产列表 |
| `blender_get_scene` | ✅ | ❌ | ✅ | 场景级全局信息 |
| `blender_get_collections` | ✅ | ❌ | ✅ | 集合层级树 |
| `blender_get_armature_data` | ✅ | ❌ | ✅ | 骨架/骨骼层级/约束/姿态 |
| `blender_get_images` | ✅ | ❌ | ✅ | 纹理/图片资产列表 |
| `blender_capture_viewport` | ✅ | ❌ | ✅ | 视口截图 |
| `blender_get_selection` | ✅ | ❌ | ✅ | 当前选择/模式/活动对象 |

---

## blender_get_objects

**用途**：列出场景中的对象，支持多种过滤条件。

**何时使用**：
- 首次调用了解场景中有哪些对象
- 查找特定类型的对象（如所有灯光、所有网格）
- 获取当前选中或可见的对象列表

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `type_filter` | string | 否 | — | 过滤对象类型：`MESH`, `LIGHT`, `CAMERA`, `CURVE`, `EMPTY`, `ARMATURE`, `LATTICE`, `FONT`, `GPENCIL`, `SPEAKER`, `VOLUME` |
| `collection` | string | 否 | — | 按集合名称过滤 |
| `selected_only` | boolean | 否 | `false` | 仅返回当前选中的对象 |
| `visible_only` | boolean | 否 | `false` | 仅返回视口中可见的对象 |
| `name_pattern` | string | 否 | — | Glob 模式过滤名称（如 `'SM_*'` 或 `'*_high'`） |

**示例**：

```json
// 列出所有对象
{"name": "List all objects"}

// 仅列出网格对象
{"name": "List mesh objects only", "type_filter": "MESH"}

// 仅列出当前选中的对象
{"name": "Get selected objects", "selected_only": true}

// 列出特定集合中的对象
{"name": "List objects in collection", "collection": "Props"}

// 按名称模式过滤
{"name": "List high-poly objects", "name_pattern": "*_high"}
```

---

## blender_get_object_data

**用途**：获取单个对象的详细数据。

**何时使用**：
- 需要深入了解某个对象的属性
- 检查对象的修改器、材质、约束等
- 读取对象的变换、物理属性等

**何时不使用**：
- 只需要对象列表 → 使用 `blender_get_objects`
- 需要骨架骨骼数据 → 使用 `blender_get_armature_data`
- 需要节点树结构 → 使用 `blender_get_node_tree`

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `name` | string | ✅ | — | 对象名称 |
| `include` | array | 否 | `["summary"]` | 包含的数据部分：`summary`, `mesh_stats`, `modifiers`, `materials`, `constraints`, `physics`, `animation`, `custom_properties`, `vertex_groups`, `shape_keys`, `uv_maps`, `particle_systems` |

**示例**：

```json
// 快速概览
{"name": "Get object summary", "include": ["summary"]}

// 检查修改器
{"name": "Check modifiers", "include": ["summary", "modifiers"]}

// 检查材质和 UV
{"name": "Check materials and UV", "include": ["materials", "uv_maps"]}

// 获取所有数据
{"name": "Get all data", "include": ["summary", "mesh_stats", "modifiers", "materials", "constraints", "physics", "animation", "custom_properties", "vertex_groups", "shape_keys", "uv_maps", "particle_systems"]}
```

---

## blender_get_node_tree

**用途**：读取任意节点树的结构（着色器、合成器、几何节点）。

**何时使用**：
- 了解材质节点结构
- 查看合成器节点连接
- 检查几何节点设置

**何时不使用**：
- 只需要基础材质属性 → 使用 `blender_get_materials`
- 需要编辑节点 → 使用 `blender_edit_nodes`

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `tree_type` | string | ✅ | — | 节点树类型：`SHADER`, `COMPOSITOR`, `GEOMETRY` |
| `context` | string | ✅ | — | 节点树上下文。`SHADER`: `OBJECT`, `WORLD`, `LINESTYLE`；`COMPOSITOR`: `SCENE`；`GEOMETRY`: `MODIFIER`, `TOOL` |
| `target` | string | 否 | — | 目标名称。`SHADER/OBJECT`: 材质名称；`SHADER/WORLD`: 世界名称（默认活动世界）；`GEOMETRY/MODIFIER`: `ObjectName/ModifierName`；`GEOMETRY/TOOL`: 工具资产名称 |
| `depth` | string | 否 | `"summary"` | 详细程度：`summary`（仅节点名称和类型），`full`（所有参数和连接） |

**示例**：

```json
// 读取对象材质节点树（摘要）
{"name": "Read object material nodes", "tree_type": "SHADER", "context": "OBJECT", "target": "Material", "depth": "summary"}

// 读取世界环境节点树（完整）
{"name": "Read world nodes", "tree_type": "SHADER", "context": "WORLD", "depth": "full"}

// 读取合成器节点
{"name": "Read compositor nodes", "tree_type": "COMPOSITOR", "context": "SCENE"}

// 读取几何节点修改器
{"name": "Read geometry nodes", "tree_type": "GEOMETRY", "context": "MODIFIER", "target": "Cube/Subdivision"}
```

---

## blender_get_animation_data

**用途**：读取动画数据（关键帧、F-Curves、NLA 条带、驱动器、形态键）。

**何时使用**：
- 检查对象的动画状态
- 查看关键帧分布
- 了解 NLA 条带组织

**何时不使用**：
- 需要编辑动画 → 使用 `blender_edit_animation`

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `target` | string | ✅ | — | 对象名称，或 `'scene'` 表示场景级动画数据 |
| `include` | array | 否 | `["keyframes"]` | 包含的动画数据：`keyframes`, `fcurves`, `nla`, `drivers`, `shape_keys` |
| `frame_range` | array | 否 | — | 可选的 `[start, end]` 帧范围以限制关键帧数据 |

**示例**：

```json
// 检查关键帧
{"name": "Check keyframes", "target": "Cube", "include": ["keyframes"]}

// 检查 NLA 条带
{"name": "Check NLA strips", "target": "Cube", "include": ["nla"]}

// 检查驱动器
{"name": "Check drivers", "target": "Cube", "include": ["drivers"]}

// 获取场景级动画数据
{"name": "Get scene animation", "target": "scene", "include": ["keyframes", "fcurves"]}

// 限制帧范围
{"name": "Get keyframes in range", "target": "Cube", "include": ["keyframes"], "frame_range": [1, 100]}
```

---

## blender_get_materials

**用途**：列出所有材质及其基本属性。

**何时使用**：
- 了解场景中有哪些材质
- 检查材质的使用状态
- 查找未使用的材质

**何时不使用**：
- 需要节点树结构 → 使用 `blender_get_node_tree`（tree_type=SHADER）

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `filter` | string | 否 | `"all"` | 过滤材质：`all`, `used_only`, `unused_only` |
| `name_pattern` | string | 否 | — | Glob 模式过滤名称（如 `'*Metal*'`） |

**示例**：

```json
// 列出所有材质
{"name": "List all materials", "filter": "all"}

// 仅列出使用的材质
{"name": "List used materials", "filter": "used_only"}

// 列出未使用的材质
{"name": "List unused materials", "filter": "unused_only"}

// 按名称模式过滤
{"name": "List metal materials", "name_pattern": "*Metal*"}
```

---

## blender_get_scene

**用途**：获取场景级全局信息。

**何时使用**：
- 了解场景的基本信息
- 检查渲染设置
- 查看时间轴配置

**何时不使用**：
- 需要配置场景 → 使用 `blender_setup_scene`

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `include` | array | 否 | `["stats", "render", "timeline"]` | 包含的节：`stats`, `render`, `world`, `timeline`, `version`, `memory` |

**示例**：

```json
// 默认信息（统计、渲染、时间线）
{"name": "Get default scene info"}

// 获取渲染设置
{"name": "Get render settings", "include": ["render"]}

// 获取世界环境
{"name": "Get world environment", "include": ["world"]}

// 获取完整信息
{"name": "Get complete scene info", "include": ["stats", "render", "world", "timeline", "version", "memory"]}
```

---

## blender_get_collections

**用途**：返回集合的层级树。

**何时使用**：
- 了解场景的组织结构
- 查找特定集合
- 检查集合的可见性

**何时不使用**：
- 需要编辑集合 → 使用 `blender_manage_collection`

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `root` | string | 否 | — | 从此集合开始。默认：场景集合（根） |
| `depth` | integer | 否 | `10` | 树的最大递归深度 |

**示例**：

```json
// 获取完整集合树
{"name": "Get collection tree"}

// 从特定集合开始
{"name": "Get subtree", "root": "Props"}

// 限制深度
{"name": "Get shallow tree", "depth": 3}
```

---

## blender_get_armature_data

**用途**：读取骨架/骨骼数据（层级、约束、姿态等）。

**何时使用**：
- 了解骨骼层级结构
- 检查骨骼约束
- 查看姿态数据

**何时不使用**：
- 只需要对象基本数据 → 使用 `blender_get_object_data`
- 需要编辑骨架 → 使用 `blender_modify_object`

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `armature_name` | string | ✅ | — | 骨架对象名称 |
| `include` | array | 否 | `["hierarchy"]` | 包含的数据部分：`hierarchy`, `poses`, `constraints`, `bone_groups`, `ik_chains` |
| `bone_filter` | string | 否 | — | Glob 模式过滤骨骼名称（如 `'Arm*'` 或 `'*_L'`） |

**示例**：

```json
// 获取骨骼层级
{"name": "Get bone hierarchy", "armature_name": "Armature", "include": ["hierarchy"]}

// 检查约束
{"name": "Check constraints", "armature_name": "Armature", "include": ["hierarchy", "constraints"]}

// 查看姿态
{"name": "View poses", "armature_name": "Armature", "include": ["poses"]}

// 过滤骨骼
{"name": "Get left arm bones", "armature_name": "Armature", "bone_filter": "*_L"}
```

---

## blender_get_images

**用途**：列出所有图片/纹理资产。

**何时使用**：
- 管理纹理资产
- 检测缺失的纹理文件
- 查找未使用的图片

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `filter` | string | 否 | `"all"` | 过滤图片：`all`, `packed`, `external`, `missing`, `unused` |
| `name_pattern` | string | 否 | — | Glob 模式过滤名称 |

**示例**：

```json
// 列出所有图片
{"name": "List all images", "filter": "all"}

// 查找缺失的纹理
{"name": "Find missing textures", "filter": "missing"}

// 列出打包的图片
{"name": "List packed images", "filter": "packed"}
```

---

## blender_capture_viewport

**用途**：捕获当前 3D 视口的截图。

**何时使用**：
- LLM 需要查看视觉结果
- 验证操作效果

**参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|-------|------|
| `shading` | string | 否 | `"SOLID"` | 视口着色模式：`SOLID`, `MATERIAL`, `RENDERED`, `WIREFRAME` |
| `camera_view` | boolean | 否 | `false` | 如果为 true，从活动相机视角捕获 |
| `format` | string | 否 | `"PNG"` | 图像格式：`PNG`, `JPEG` |

**示例**：

```json
// 默认截图（SOLID 模式）
{"name": "Capture viewport"}

// 渲染视图截图
{"name": "Rendered view", "shading": "RENDERED"}

// 相机视角
{"name": "Camera view", "camera_view": true}

// 线框模式
{"name": "Wireframe view", "shading": "WIREFRAME"}
```

---

## blender_get_selection

**用途**：返回当前选择状态。

**何时使用**：
- 了解用户当前正在操作什么
- 检查当前编辑模式

**参数**：

无参数

**返回值示例**：

```json
{
  "selected_objects": ["Cube", "Sphere"],
  "active_object": "Cube",
  "mode": "OBJECT",
  "tool": "builtin.select_box"
}
```

**示例**：

```json
// 获取当前选择
{"name": "Get selection state"}
```
