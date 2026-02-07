# 声明式写入层工具 (Declarative Write Layer)

声明式写入层提供 3 个工具，让 LLM 以声明式、批处理方式编辑 Blender 的复杂系统（节点编辑器、动画、视频序列编辑器）。

## 工具列表

| 工具 | readOnly | destructive | idempotent | 说明 |
|-----|---------|------------|------------|------|
| `blender_edit_nodes` | ❌ | ❌ | ❌ | 编辑任意节点树（add/remove/connect/disconnect/set_value）⭐ 核心 |
| `blender_edit_animation` | ❌ | ❌ | ❌ | 编辑动画（keyframe/NLA/driver/shape_key/frame_range） |
| `blender_edit_sequencer` | ❌ | ❌ | ❌ | 编辑 VSE 视频序列（strip/transition/effect） |

---

## blender_edit_nodes

**用途**：编辑任意节点树 — 添加/删除节点、连接/断开、设置输入值和属性。支持 6 种节点树上下文：对象着色器、世界着色器、线条样式着色器、场景合成器、几何节点修改器、几何节点工具。

**何时使用**：
- 创建或编辑着色器材质
- 设置合成器节点图
- 配置几何节点
- **这是 LLM 最重要的节点编辑工具**

**何时不使用**：
- 只需要基础 PBR 属性 → 使用 `blender_manage_material`
- 需要读取节点树 → 使用 `blender_get_node_tree`

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| `tree_type` | string | ✅ | 节点树类型：`SHADER`, `COMPOSITOR`, `GEOMETRY` |
| `context` | string | ✅ | 节点树上下文。`SHADER`: `OBJECT`, `WORLD`, `LINESTYLE`；`COMPOSITOR`: `SCENE`；`GEOMETRY`: `MODIFIER`, `TOOL` |
| `target` | string | 否 | 目标名称。`SHADER/OBJECT`: 材质名称；`SHADER/WORLD`: 世界名称（默认活动世界）；`SHADER/LINESTYLE`: 线条样式名称；`GEOMETRY/MODIFIER`: `ObjectName/ModifierName`；`GEOMETRY/TOOL`: 工具资产名称；`COMPOSITOR/SCENE`: 省略或场景名称 |
| `operations` | array | ✅ | 节点操作数组，按顺序执行 |

**operations 数组项**：

每个操作都是一个对象，必须包含 `action` 字段。其他字段取决于 `action` 类型。

| action | 必需字段 | 可选字段 | 说明 |
|--------|---------|---------|------|
| `add_node` | `type`, `name`, `location` | — | 添加节点 |
| `remove_node` | `name` | — | 删除节点 |
| `connect` | `from_node`, `from_socket`, `to_node`, `to_socket` | — | 连接两个节点的插座 |
| `disconnect` | `node`, `input` | — | 断开节点输入 |
| `set_value` | `node`, `input`, `value` | — | 设置节点输入值 |
| `set_property` | `node`, `property`, `value` | — | 设置节点属性 |

**示例**：

```json
// 创建基础着色器材质
{
  "tree_type": "SHADER",
  "context": "OBJECT",
  "target": "Material",
  "operations": [
    {
      "action": "add_node",
      "type": "ShaderNodeBsdfPrincipled",
      "name": "Principled BSDF",
      "location": [0, 0]
    },
    {
      "action": "add_node",
      "type": "ShaderNodeOutputMaterial",
      "name": "Material Output",
      "location": [300, 0]
    },
    {
      "action": "connect",
      "from_node": "Principled BSDF",
      "from_socket": "BSDF",
      "to_node": "Material Output",
      "to_socket": "Surface"
    },
    {
      "action": "set_value",
      "node": "Principled BSDF",
      "input": "Base Color",
      "value": [0.8, 0.2, 0.2, 1.0]
    }
  ]
}

// 设置混合材质
{
  "tree_type": "SHADER",
  "context": "OBJECT",
  "target": "Material",
  "operations": [
    {
      "action": "add_node",
      "type": "ShaderNodeMixRGB",
      "name": "Mix",
      "location": [200, 0]
    },
    {
      "action": "set_value",
      "node": "Mix",
      "input": "Color A",
      "value": [1.0, 0.0, 0.0, 1.0]
    },
    {
      "action": "set_value",
      "node": "Mix",
      "input": "Color B",
      "value": [0.0, 0.0, 1.0, 1.0]
    },
    {
      "action": "set_value",
      "node": "Mix",
      "input": "Fac",
      "value": 0.5
    }
  ]
}

// 几何节点分布
{
  "tree_type": "GEOMETRY",
  "context": "MODIFIER",
  "target": "Cube/GeometryNodes",
  "operations": [
    {
      "action": "add_node",
      "type": "GeometryNodeDistributePointsOnFaces",
      "name": "Distribute Points",
      "location": [0, 0]
    },
    {
      "action": "set_value",
      "node": "Distribute Points",
      "input": "Distance Min",
      "value": 0.1
    }
  ]
}

// 合成器眩光效果
{
  "tree_type": "COMPOSITOR",
  "context": "SCENE",
  "operations": [
    {
      "action": "add_node",
      "type": "CompositorNodeGlare",
      "name": "Glare",
      "location": [400, 0]
    },
    {
      "action": "set_property",
      "node": "Glare",
      "property": "threshold",
      "value": 0.5
    }
  ]
}
```

---

## blender_edit_animation

**用途**：编辑动画数据 — 插入/修改/删除关键帧、管理 NLA 条带、设置驱动器、控制形态键、配置时间轴设置。

**何时使用**：
- 添加关键帧
- 管理 NLA 动画条带
- 设置驱动器
- 编辑形态键

**何时不使用**：
- 需要读取动画数据 → 使用 `blender_get_animation_data`

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| `action` | string | ✅ | 动画操作：`insert_keyframe`, `delete_keyframe`, `modify_keyframe`, `add_nla_strip`, `modify_nla_strip`, `remove_nla_strip`, `add_driver`, `remove_driver`, `set_shape_key`, `set_frame`, `set_frame_range` |
| `object_name` | string | 否 | 目标对象名称 |
| `data_path` | string | 否 | 关键帧/驱动器的属性路径（如 `'location'`, `'rotation_euler'`, `'scale'`, `'energy'`, 或自定义路径如 `modifiers["Subsurf"].levels`） |
| `index` | integer | 否 | 属性的数组索引（-1 表示所有通道，0/1/2 表示 X/Y/Z） |
| `frame` | integer | 否 | 关键帧操作的帧号 |
| `value` | — | 否 | 关键帧或形态键的值（number, array, 或 boolean） |
| `interpolation` | string | 否 | 关键帧插值类型：`CONSTANT`, `LINEAR`, `BEZIER`, `SINE`, `QUAD`, `CUBIC`, `QUART`, `QUINT`, `EXPO`, `CIRC`, `BACK`, `BOUNCE`, `ELASTIC` |
| `nla_action` | string | 否 | NLA 条带操作的 Action 名称 |
| `nla_start_frame` | integer | 否 | NLA 条带的开始帧 |
| `nla_strip_name` | string | 否 | 修改/删除 NLA 条带时的条带名称 |
| `driver_expression` | string | 否 | 驱动器的 Python 表达式（如 `'frame * 0.1'`, `'var + 5'`） |
| `shape_key_name` | string | 否 | `set_shape_key` 操作的形态键名称 |
| `fps` | number | 否 | 每秒帧数（用于 `set_frame_range`） |
| `frame_start` | integer | 否 | 开始帧（用于 `set_frame_range` 或 `set_frame`） |
| `frame_end` | integer | 否 | 结束帧（用于 `set_frame_range`） |

**示例**：

```json
// 插入位置关键帧
{
  "action": "insert_keyframe",
  "object_name": "Cube",
  "data_path": "location",
  "frame": 1,
  "value": [0, 0, 0],
  "interpolation": "BEZIER"
}

// 插入旋转关键帧
{
  "action": "insert_keyframe",
  "object_name": "Cube",
  "data_path": "rotation_euler",
  "frame": 25,
  "value": [0, 0.785, 0]
}

// 添加 NLA 条带
{
  "action": "add_nla_strip",
  "nla_action": "WalkCycle",
  "nla_start_frame": 1
}

// 添加驱动器
{
  "action": "add_driver",
  "object_name": "Light",
  "data_path": "energy",
  "driver_expression": "frame * 10"
}

// 设置形态键
{
  "action": "set_shape_key",
  "object_name": "Character",
  "shape_key_name": "Smile",
  "value": 0.5
}

// 设置当前帧
{
  "action": "set_frame",
  "frame": 50
}

// 设置帧范围和 FPS
{
  "action": "set_frame_range",
  "frame_start": 1,
  "frame_end": 250,
  "fps": 24
}
```

---

## blender_edit_sequencer

**用途**：编辑视频序列编辑器（VSE）— 添加/修改/删除条带，添加转场和特效。支持视频、图像、音频、文本、颜色和调整层条带。

**何时使用**：
- 添加视频/图像/音频条带
- 添加转场效果
- 添加特效（眩光、模糊等）

**何时不使用**：
- 需要节点级合成 → 使用 `blender_edit_nodes`（tree_type=COMPOSITOR）

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| `action` | string | ✅ | 序列编辑器操作：`add_strip`, `modify_strip`, `delete_strip`, `add_effect`, `add_transition`, `move_strip` |
| `strip_type` | string | 否 | 条带类型（`add_strip` 操作）：`VIDEO`, `IMAGE`, `AUDIO`, `TEXT`, `COLOR`, `ADJUSTMENT` |
| `filepath` | string | 否 | VIDEO/IMAGE/AUDIO 条带的文件路径 |
| `channel` | integer | 否 | VSE 通道号 |
| `frame_start` | integer | 否 | 条带的开始帧 |
| `frame_end` | integer | 否 | 条带的结束帧 |
| `strip_name` | string | 否 | 修改/删除/移动条带时的条带名称 |
| `text` | string | 否 | TEXT 条带的文本内容 |
| `font_size` | number | 否 | TEXT 条带的字体大小 |
| `color` | array | 否 | TEXT/COLOR 条带的颜色 [r,g,b] 或 [r,g,b,a] |
| `effect_type` | string | 否 | 特效类型（`add_effect` 操作）：`TRANSFORM`, `SPEED`, `GLOW`, `GAUSSIAN_BLUR`, `COLOR_BALANCE`, `ALPHA_OVER`, `ALPHA_UNDER`, `MULTIPLY` |
| `transition_type` | string | 否 | 转场类型（`add_transition` 操作）：`CROSS`, `WIPE`, `GAMMA_CROSS` |
| `transition_duration` | integer | 否 | 转场的持续时间（帧数） |
| `settings` | object | 否 | 条带/特效类型的特定设置 |

**示例**：

```json
// 添加视频条带
{
  "action": "add_strip",
  "strip_type": "VIDEO",
  "filepath": "/path/to/video.mp4",
  "channel": 1,
  "frame_start": 1,
  "frame_end": 250
}

// 添加音频条带
{
  "action": "add_strip",
  "strip_type": "AUDIO",
  "filepath": "/path/to/audio.mp3",
  "channel": 2,
  "frame_start": 1,
  "frame_end": 250
}

// 添加文本条带
{
  "action": "add_strip",
  "strip_type": "TEXT",
  "text": "Hello World",
  "font_size": 100,
  "color": [1, 1, 1, 1],
  "channel": 3,
  "frame_start": 1,
  "frame_end": 50
}

// 添加颜色条带
{
  "action": "add_strip",
  "strip_type": "COLOR",
  "color": [0.5, 0.5, 0.5, 1],
  "channel": 1,
  "frame_start": 1,
  "frame_end": 100
}

// 添加转场
{
  "action": "add_transition",
  "transition_type": "CROSS",
  "transition_duration": 24
}

// 添加眩光特效
{
  "action": "add_effect",
  "effect_type": "GLOW",
  "settings": {
    "threshold": 0.5,
    "size": 20
  }
}

// 删除条带
{
  "action": "delete_strip",
  "strip_name": "video.mp4"
}
```

---

## 工作流示例

### 创建完整着色器材质

1. 使用 `blender_get_node_tree` 了解现有节点结构
2. 使用 `blender_edit_nodes` 添加、连接、配置节点
3. 使用 `blender_capture_viewport` 验证结果

### 设置动画循环

1. 使用 `blender_get_animation_data` 检查现有关键帧
2. 使用 `blender_edit_animation` 插入关键帧
3. 使用 `blender_edit_animation` 添加 NLA 条带组织动画

### 编辑视频

1. 使用 `blender_edit_sequencer` 添加视频/音频条带
2. 使用 `blender_edit_sequencer` 添加转场和特效
3. 使用 `blender_setup_scene` 配置输出设置
