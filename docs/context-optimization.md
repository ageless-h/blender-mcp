# Blender MCP 上下文优化方案

> **目标**：在 ~400K token 的上下文窗口内最大化有效工作量  
> **重心**：节点系统（Shader / Compositor / Geometry Nodes）  
> **日期**：2026-04-20

---

## 一、现状量化

### 1.1 上下文消耗全景

| 消耗来源 | 估算 Tokens | 占 400K 比例 | 可否优化 |
|----------|-------------|-------------|---------|
| **工具 Schema（29 个工具定义）** | **~10,000** | **2.5%** | ✅ 高 |
| **典型读操作响应（一次 get_node_tree full）** | **900–6,000** | **0.2–1.5%** | ✅ 高 |
| **复杂节点树读取（10+ 节点）** | **4,000–6,000** | **1.0–1.5%** | ✅ 高 |
| **blender_get_objects（大场景 100+ 物体）** | **3,000–8,000** | **0.8–2.0%** | ✅ 中 |
| **blender_get_animation_data（1000帧动画）** | **15,000–25,000** | **3.8–6.3%** | ✅ 高 |
| **blender_execute_script 输出** | **无上限** | **灾难性** | 🔴 关键 |
| **viewport_capture base64** | **5,000–50,000** | **1.3–12.5%** | ✅ 高 |
| **node_types 查询（200+ 节点类型）** | **3,000–5,000** | **0.8–1.3%** | ✅ 中 |
| **每次成功响应的固定开销**（ok/error/timing_ms） | **~15** | **微量×N** | ✅ 低 |
| **累计 N 次工具调用** | **N × 平均响应** | **核心问题** | ✅ 架构级 |

**核心矛盾**：一次典型的节点编辑工作流需要 read → edit → read 验证，3 次调用消耗约 3,000–15,000 tokens。在 400K 窗口内，加上 LLM 自身的推理 token，**有效工具调用次数约 30–60 次**。复杂场景搭建可能需要 100+ 次调用。

### 1.2 最大上下文消耗来源排名

| 排名 | 来源 | 单次最大 Token | 频率 | 总影响 |
|------|------|---------------|------|--------|
| 1 | `blender_execute_script` 输出 | **无上限** | 低 | 🔴 灾难 |
| 2 | `viewport_capture` base64 | ~50,000 | 中 | 🔴 严重 |
| 3 | `blender_get_animation_data` keyframes | ~25,000 | 中 | 🔴 严重 |
| 4 | 工具 Schema 常驻 | ~10,000 | 100% | ⚠️ 固定税 |
| 5 | `blender_get_node_tree` full 模式 | ~6,000 | 高 | ⚠️ 累积 |
| 6 | `node_types` 查询 | ~5,000 | 低 | ⚠️ 单次 |
| 7 | `blender_get_objects` 大场景 | ~8,000 | 中 | ⚠️ 累积 |

---

## 二、优化方案

### P0 — 关键（可减少 30–50% 上下文消耗）

#### 2.1 响应截断守卫

**问题**：`blender_execute_script` 的 `output` 和 `return_value` 完全无界，一次失控的 `print()` 可吞噬整个上下文窗口。

**方案**：在 `mcp_protocol.py` 的 `tools_call()` 返回前，对序列化后的 JSON 文本做硬截断：

```python
MAX_RESPONSE_CHARS = 30_000  # 约 7,500 tokens

text = json.dumps(result.result)
if len(text) > MAX_RESPONSE_CHARS:
    text = text[:MAX_RESPONSE_CHARS] + f'\n... [truncated, {len(text)} total chars]'
```

**影响范围**：所有工具响应  
**预期收益**：防止灾难性上下文爆炸  
**风险**：截断可能破坏 JSON 结构 → LLM 需理解截断标记

---

#### 2.2 节点树读取：引入 `"topology"` 深度级别

**问题**：当前只有 `summary`（无连接信息，太少）和 `full`（所有默认值都返回，太多）。LLM 在编辑节点前最需要知道的是**拓扑结构**（哪些节点通过哪些 socket 连接），而不是每个未修改 input 的默认值。

**方案**：在 `reader.py` 中新增 `depth="topology"` 模式：

```python
# depth="topology" — 只返回已连接的 socket 和非默认值 input
{
    "tree_type": "SHADER",
    "nodes": [
        {
            "name": "Principled BSDF",
            "type": "ShaderNodeBsdfPrincipled",
            # 无 label（当 label == name 时省略）
            # 无 location（拓扑模式不关心布局）
            "inputs": [
                # 仅返回：已连接 OR 值 ≠ 默认值的 input
                {"name": "Base Color", "value": [0.2, 0.5, 0.8, 1.0]},  # 非默认
                {"name": "Roughness", "is_linked": true}                 # 已连接
            ],
            "outputs": [
                {"name": "BSDF", "is_linked": true}  # 仅已连接
            ]
        }
    ],
    "links": [...]
}
```

**预期收益**：
- Principled BSDF 默认材质：从 ~1,000 tokens 降到 ~200 tokens（**-80%**）
- 10 节点复杂材质：从 ~5,000 tokens 降到 ~1,500 tokens（**-70%**）

---

#### 2.3 节点树读取：`skip_defaults` 参数

**问题**：`depth="full"` 返回所有 26 个 Principled BSDF 输入，其中 ~20 个保持默认值。

**方案**：在 `blender_get_node_tree` 工具 schema 和 `reader.py` 中添加 `skip_defaults` 布尔参数（默认 `true`）：

- 对于每个 input socket，对比 `default_value` 与 Blender 的出厂默认值
- 若值未改变且未连接，从响应中省略
- 对于 `properties`，跳过等于 RNA schema 默认值的属性

**实现方式**：
```python
# reader.py — _read_inputs() 中
for inp in node.inputs:
    if skip_defaults and not inp.is_linked:
        if _is_default_value(inp):
            continue
    inputs.append({...})
```

**预期收益**：`full` 模式响应减少 50–70%

---

#### 2.4 精简响应信封

**问题**：每个成功响应都包含 `"ok": true, "error": null, "timing_ms": 0.123456789`。

**方案**：
- 成功时只返回 `{"result": {...}}`，省略 `ok` 和 `error`
- 失败时只返回 `{"error": {...}}`，省略 `ok` 和 `result`  
- `timing_ms` 四舍五入到整数（`1` 而不是 `1.23456789`），或完全移至调试日志
- 移除 `error.suggestion` 中的固定建议文本（这些文本每次都重复传输）

**预期收益**：每次响应减少 ~30–50 字符，30+ 次调用累计 ~250–400 tokens

---

#### 2.5 edit_nodes 返回紧凑确认

**问题**：`blender_edit_nodes` 执行后的响应结构待确认，但通常写操作后 LLM 会再次调用 `get_node_tree` 验证，形成 write → read 循环。

**方案**：让 `edit_nodes` 返回精简的变更摘要，使 LLM 不需要立即 re-read：

```python
{
    "operations_completed": 5,
    "nodes_added": ["Noise Texture", "ColorRamp"],
    "connections_made": 2,
    "values_set": ["Noise Texture.Scale = 5.0"]
}
```

而不是返回完整的节点树快照。LLM 只需确认操作成功即可，不需要重新读取整个树。

**预期收益**：避免一次 read 调用，节省 ~1,000–5,000 tokens

---

### P1 — 高优先级（可减少 15–25% 上下文消耗）

#### 2.6 工具 Schema 瘦身

**问题**：29 个工具定义占 ~10,000 tokens 常驻上下文，其中 `blender_edit_nodes` 单独占 11%（~4,446 字符）。

**方案**：

**a) 压缩枚举描述**：
- `modifier_type` 的 37 个枚举值 → 移到描述文本中用逗号分隔列举，不用 JSON Schema `enum`
- `constraint_type` 的 22 个枚举值 → 同上
- `import_export.format` 的 13 个值 → 同上

**b) 合并重复的参数描述**：
- `context` 和 `target` 参数描述在 `get_node_tree` 和 `edit_nodes` 中完全相同 → 考虑缩短

**c) 压缩 `blender_edit_nodes` 的 `operations` schema**：
- 当前每个 operation 有 ~20 个可选参数，每个都带完整描述
- 压缩策略：将不常用的 action（`set_color_ramp_element`, `add_color_ramp_element`, `remove_color_ramp_element`, `set_curve_mapping_point`, `add_interface_socket`, `remove_interface_socket`）的参数描述缩到最短

**d) 移除 `annotations` 中的 `title` 字段**：
- `title` 已由 `description` 覆盖，且 MCP 协议不强制要求

**预期收益**：工具 Schema 从 ~10,000 降到 ~7,000 tokens（**-30%**）

---

#### 2.7 `blender_get_objects` 响应瘦身

**问题**：`list_items()` 每个物体返回 `location: [x,y,z]`（3 个浮点数），多数情况下 LLM 不需要精确坐标。

**方案**：
- 默认不返回 `location`；增加 `include_location=true` 参数控制
- `selected` 和 `visible` 仅在非默认值时返回（`selected=false` 和 `visible=true` 省略）

**预期收益**：100 个物体的列表从 ~3,000 tokens 降到 ~1,500 tokens（**-50%**）

---

#### 2.8 `blender_get_animation_data` 分页/摘要

**问题**：keyframes 数组完全无界，1000 帧动画可返回 6000+ 条记录。

**方案**：
- 默认返回摘要模式：每条 fcurve 只返回 `{data_path, index, keyframe_count, frame_range: [min, max]}`
- 增加 `keyframe_detail=true` 参数返回全部关键帧
- 增加 `max_keyframes=100` 参数，超出时截断并标记 `"truncated": true`

**预期收益**：动画数据从 ~25,000 tokens 降到 ~500 tokens（默认摘要模式，**-98%**）

---

#### 2.9 消除冗余 `count` 字段

**问题**：多个 handler 同时返回列表和列表长度：
- `CollectionHandler`: `objects: [...]` + `objects_count`
- `GreasePencilHandler`: `layers: [...]` + `layers_count`
- `node_tree_read()`: `nodes: [...]` + `node_count`
- `GenericCollectionHandler.list_items()`: `items: [...]` + `count`

**方案**：全部移除冗余 `count` / `*_count` 字段。LLM 和 JSON 解析器都能从数组长度获取计数。

**预期收益**：每次响应减少 ~20–50 字符（累积可观）

---

#### 2.10 `label` 字段去重

**问题**：节点和材质节点的 `label` 字段在绝大多数情况下等于 `name`（用户未自定义）。

**方案**：仅当 `label != name` 且 `label != ""` 时才返回 `label`。

**预期收益**：每个节点减少 ~20–40 字符

---

### P2 — 中优先级（可减少 5–10% 上下文消耗）

#### 2.11 `location` 字段策略

**问题**：节点的 `location: [x, y]` 对 LLM 理解节点逻辑无意义。物体的 `location: [x, y, z]` 在列表中也通常不需要。

**方案**：
- `get_node_tree`：`summary` 和 `topology` 模式不返回 `location`，仅 `full` 模式返回
- `get_objects`：增加 `include_transform` 参数，默认 `false`

---

#### 2.12 省略默认值属性

**问题**：多个 handler 返回大量保持默认值的属性：

| Handler | 字段 | 默认值 | 出现频率 |
|---------|------|--------|---------|
| CameraHandler | `shift_x`, `shift_y` | 0.0 | ~99% |
| CameraHandler | `dof_focus_distance` | 10.0 | ~95% |
| CameraHandler | `sensor_width/height` | 36.0/24.0 | ~90% |
| LightHandler | `specular_factor` | 1.0 | ~95% |
| CollectionHandler | `hide_render`, `color_tag` | false, "NONE" | ~90% |
| ModifierHandler | `show_in_editmode`, `show_render` | false, true | ~80% |
| MaterialHandler | `blend_method`, `shadow_method` | "OPAQUE" | ~85% |
| ImageHandler | `channels`, `depth`, `is_float` | 4, 32, false | ~95% |

**方案**：实现通用的 `_omit_defaults()` 工具函数：

```python
def _omit_defaults(data: dict, defaults: dict) -> dict:
    """移除与默认值相同的字段"""
    return {k: v for k, v in data.items() if k not in defaults or v != defaults[k]}
```

**预期收益**：各 handler 响应减少 20–40%

---

#### 2.13 MaterialHandler 按需加载 nodes

**问题**：`MaterialHandler.read()` 无条件返回所有节点列表（`nodes: [{name, type, label}]`），复杂材质可有 50+ 节点。

**方案**：仿照 `ObjectHandler` 的 `include` 模式，默认不返回 `nodes`，只返回 `nodes_count`。

---

#### 2.14 ArmatureHandler 默认精简

**问题**：默认包含 `hierarchy` 数组，每个骨骼 6 个浮点数（head/tail），大型骨架可有 100+ 骨骼。

**方案**：默认只返回 `bones_count` 和扁平的骨骼名称列表；`hierarchy` 改为 `include=["hierarchy"]` 时才展开。

---

#### 2.15 NodeTreeHandler（bpy.data 查询）精简

**问题**：`NodeTreeHandler.read()` 无条件返回所有 `nodes` 和 `links`（不同于 `blender_get_node_tree` 工具的 depth 控制）。

**方案**：与节点 reader 统一，默认返回 `nodes_count` 和 `links_count`，节点列表按需展开。

---

### P3 — 低优先级（架构级优化）

#### 2.16 工具动态注册（MCP 协议层面）

**问题**：29 个工具定义全部注入上下文，但单次会话通常只用 5–8 个工具。

**方案**：利用 MCP 协议的 `tools/list` 支持，实现动态工具集：
- 初始只注册核心工具（~10 个最常用）
- 当需要特定领域工具时通过 LLM 自主发现或用户提示触发
- 使用 MCP 的 `notifications/tools/list_changed` 通知客户端刷新

**分层建议**：

| 层级 | 工具 | 始终加载 |
|------|------|---------|
| 核心 | get_objects, get_object_data, get_node_tree, edit_nodes, create_object, modify_object, get_scene | ✅ |
| 材质 | get_materials, manage_material | 按需 |
| 动画 | get_animation_data, edit_animation | 按需 |
| 场景 | get_collections, setup_scene, manage_collection | 按需 |
| 高级 | edit_sequencer, manage_constraints, manage_physics, manage_uv, edit_mesh | 按需 |
| 兜底 | execute_operator, execute_script, import_export, render_scene, batch_execute | 按需 |

**预期收益**：工具 Schema 从 ~10,000 降到 ~5,000 tokens（**-50%**）  
**风险**：需要客户端支持动态工具列表更新；部分 MCP 客户端可能缓存工具列表

---

#### 2.17 批量操作减少往返

**问题**：创建一个完整材质通常需要 5–10 次 `blender_edit_nodes` 调用（每次添加 1–3 个节点），每次调用消耗请求 + 响应的上下文。

**方案**：`blender_edit_nodes` 已支持 `operations` 数组批量操作。优化重点在于：
- 增加 `return_tree=false` 参数，批量操作后不返回完整节点树
- 允许操作间引用（如 `add_node` 返回的名称可在后续 `connect` 中使用） — 已通过 `name` 参数支持

**已有能力**：`blender_batch_execute` 工具支持跨工具批量调用。但其 schema 定义本身也消耗额外 token。

---

#### 2.18 响应压缩/引用机制

**问题**：多次 `get_node_tree` 调用返回大量重复数据（未变更的节点重复出现）。

**方案（长期）**：
- **增量响应**：读取时附带 `since_version` 参数，只返回变更的节点
- **节点 hash**：每个节点返回 content hash，LLM 可对比前后 hash 判断是否需要详细数据
- **引用缓存**：MCP 协议层维护最近 N 次读取的 hash，相同数据返回引用标记

**复杂度**：高，需要 addon 端维护版本状态  
**预期收益**：重复读取场景减少 60–80%

---

## 三、节点系统专项优化

节点操作是当前工作重心，以下是针对性优化：

### 3.1 节点读取分级

| 级别 | 数据范围 | 典型 Token | 适用场景 |
|------|---------|-----------|---------|
| `summary` | 节点名+类型 | ~100 | 快速概览"有哪些节点" |
| `topology`（新增） | 已连接 socket + 非默认值 | ~200–500 | **编辑前理解节点图结构** |
| `full` + `skip_defaults` | 全部但跳过默认值 | ~500–2,000 | 需要精确值时 |
| `full` | 所有数据 | ~1,000–6,000 | 调试/完整导出 |

### 3.2 节点类型查询优化

**问题**：`node_types` 查询返回 200+ 条记录，但 LLM 通常只需要特定类别。

**方案**：
- 已有 `prefix` 过滤 — **强制要求 `prefix` 参数**（如 `ShaderNode`, `CompositorNode`, `GeometryNode`）
- 增加 `max_results=20` 参数
- 返回格式从 `[{bl_idname, name}]` 精简为 `["bl_idname: name"]` 字符串数组

### 3.3 节点编辑结果优化

**当前返回**：每个 operation 的详细结果  
**优化方案**：
- 成功的操作只返回操作计数
- 只有失败的操作返回详细错误
- 增加 `return_summary=true` 参数控制

```python
# 优化后的 edit_nodes 响应
{
    "completed": 5,
    "failed": 0,
    # 仅在有失败时：
    # "errors": [{"index": 2, "action": "connect", "error": "Socket 'Color' not found"}]
}
```

### 3.4 常见节点模式模板

**长期方案**：预定义常见节点组合模板，减少逐个添加节点的往返：

```python
# 新工具：blender_apply_node_template
{
    "template": "pbr_basic",
    "material": "MyMaterial",
    "overrides": {
        "base_color": [0.8, 0.2, 0.1, 1.0],
        "roughness": 0.4
    }
}
```

**注意**：此方案需要新增工具定义，本身也占用 schema token。需权衡利弊。

---

## 四、实施优先级与收益预估

### 阶段 1（1–2 天）— 立即见效

| 编号 | 优化项 | 修改文件 | 预期收益 |
|------|--------|---------|---------|
| 2.1 | 响应截断守卫 | `mcp_protocol.py` | 防止灾难 |
| 2.4 | 精简响应信封 | `handlers/response.py` | -250 tokens/30 调用 |
| 2.9 | 移除冗余 count | 多个 handler | -500 tokens/会话 |
| 2.10 | label 去重 | `nodes/reader.py` | -200 tokens/读取 |

### 阶段 2（2–3 天）— 核心收益

| 编号 | 优化项 | 修改文件 | 预期收益 |
|------|--------|---------|---------|
| 2.2 | topology 深度级别 | `nodes/reader.py`, `schemas/tools.py` | **-70% 节点读取** |
| 2.3 | skip_defaults | `nodes/reader.py`, `schemas/tools.py` | **-50% full 模式** |
| 2.5 | edit_nodes 紧凑确认 | `nodes/editor.py` | -1,000–5,000 tokens/次 |
| 2.6 | Schema 瘦身 | `schemas/tools.py` | **-3,000 tokens 常驻** |

### 阶段 3（3–5 天）— 全面优化

| 编号 | 优化项 | 修改文件 | 预期收益 |
|------|--------|---------|---------|
| 2.7 | get_objects 瘦身 | `data/object_handler.py` | -50% 列表响应 |
| 2.8 | animation 分页 | `animation/reader.py` | -98% 默认响应 |
| 2.11 | location 策略 | 多个 handler | -20% 列表响应 |
| 2.12 | 省略默认值 | 多个 handler | -20–40% 各响应 |
| 2.13 | Material nodes 按需 | `data/material_handler.py` | -30% 材质读取 |
| 2.14 | Armature 精简 | `data/core_handlers.py` | -60% 骨架读取 |

### 阶段 4（长期）— 架构升级

| 编号 | 优化项 | 预期收益 |
|------|--------|---------|
| 2.16 | 动态工具注册 | -50% Schema 常驻 |
| 2.17 | 批量操作优化 | 减少 50% 往返 |
| 2.18 | 增量/引用响应 | -60–80% 重复读取 |

---

## 五、总体预期效果

| 指标 | 优化前 | 阶段 1 后 | 阶段 2 后 | 阶段 3 后 |
|------|--------|----------|----------|----------|
| Schema 常驻 | ~10,000 tok | ~10,000 | ~7,000 | ~7,000 |
| 单次节点读取（默认材质） | ~1,000 tok | ~950 | ~200 | ~200 |
| 单次节点读取（复杂材质） | ~5,000 tok | ~4,800 | ~1,500 | ~1,200 |
| 10 次 read+edit 循环 | ~30,000 tok | ~28,000 | ~10,000 | ~8,000 |
| 最大单次响应 | 无限 | 7,500 | 7,500 | 7,500 |
| 有效工具调用次数/会话 | ~30–60 | ~35–65 | ~60–100 | ~80–120 |

**阶段 2 完成后，同样的 400K 上下文窗口可支撑约 2 倍的有效工作量。**

---

## 六、各文件具体修改清单

### `src/blender_mcp/mcp_protocol.py`
- [x] `tools_call()`：返回前添加 `MAX_RESPONSE_CHARS` 截断
- [x] `tools_call()`：成功响应移除 `indent=2`（`MCP_PRETTY_JSON` 默认应为 false）
- [ ] `tools_list()`：考虑动态过滤（阶段 4）- 已评估，需要客户端支持，暂缓

### `src/blender_mcp/schemas/tools.py`
- [x] `blender_edit_nodes`：压缩 operations schema（缩短参数描述）
- [x] `blender_get_node_tree`：添加 `depth="topology"` 选项
- [x] `blender_get_node_tree`：添加 `skip_defaults` 参数
- [x] `blender_manage_modifier`：37 个 modifier_type 枚举移入描述文本
- [x] `blender_manage_constraints`：22 个 constraint_type 枚举移入描述文本
- [x] 所有工具：移除 `annotations.title`（如不影响客户端）
- [x] `blender_get_objects`：添加 `include_location` 参数
- [x] `blender_get_animation_data`：添加 `keyframe_detail` 和 `max_keyframes` 参数

### `src/blender_mcp_addon/handlers/response.py`
- [x] `_ok()`：移除 `"error": None`
- [x] `_error()`：移除 `"result": None`
- [x] `_ok()`：`timing_ms` 四舍五入到整数
- [ ] `_error()`：移除 `error.suggestion`（或移到日志）

### `src/blender_mcp_addon/handlers/nodes/reader.py`
- [x] 实现 `depth="topology"` 模式
- [x] 实现 `skip_defaults` 逻辑
- [x] `label` 仅在 `label != name` 且非空时返回
- [x] `summary` 和 `topology` 模式移除 `location`（仅 `full` 模式返回）
- [x] 移除 `node_count` / `link_count`（冗余）
- [x] 移除回显的 `expand_groups` / `max_depth`（已检查，响应中未包含）

### `src/blender_mcp_addon/handlers/nodes/editor.py`
- [x] 返回紧凑操作摘要而非完整结果（`completed`, `failed`, `errors`）

### `src/blender_mcp_addon/handlers/data/object_handler.py`
- [x] `list_items()`：移除 `location`，新增 `include_location` 参数
- [x] `list_items()`：`selected` 仅在 `true` 时返回，`visible` 仅在 `false` 时返回
- [x] `list_items()`：移除 `count` 字段
- [x] modifiers：省略 `show_viewport`/`show_render` 默认值

### `src/blender_mcp_addon/handlers/data/material_handler.py`
- [x] `read()`：`nodes` 改为按需包含（`include_nodes` 参数）
- [x] 省略 `blend_method`/`shadow_method` 默认值
- [x] `list_items()`：移除 `count` 字段

### `src/blender_mcp_addon/handlers/data/core_handlers.py`
- [x] `ArmatureHandler`：默认不展开 `hierarchy`，返回扁平骨骼名称列表
- [x] `CameraHandler`：省略 `shift_x`/`shift_y`/`sensor_width`/`sensor_height`/`dof_focus_distance` 默认值
- [x] `LightHandler`：省略 `specular_factor` 默认值
- [x] `GreasePencilHandler`：移除 `layers_count`，改为返回 `layers` 数量

### `src/blender_mcp_addon/handlers/data/collection_handler.py`
- [x] 移除 `objects_count`/`children_count`（有列表已足够）
- [x] 省略 `hide_viewport`/`hide_render`/`color_tag` 默认值

### `src/blender_mcp_addon/handlers/data/mesh_handler.py`
- [x] 省略 `has_custom_normals`/`is_editmode`/`loops` 默认值
- [x] 移除冗余的 `_count` 后缀

### `src/blender_mcp_addon/handlers/data/image_handler.py`
- [x] 省略 `channels`/`depth`/`is_float` 默认值

### `src/blender_mcp_addon/handlers/data/scene_handler.py`
- [x] 移除 `objects_count`，改为返回 `objects` 数量

### `src/blender_mcp_addon/handlers/data/mask_handler.py`
- [x] 移除 `layers_count`，改为返回 `layers` 数量

### `src/blender_mcp_addon/handlers/data/node_tree_handler.py`
- [x] `read()`：默认返回节点/链接计数，`include_nodes`/`include_links` 参数控制详情
- [x] `list_items()`：移除 `count` 字段

### `src/blender_mcp_addon/handlers/base.py`
- [x] `list_items()`：移除 `count` 字段

### `src/blender_mcp_addon/handlers/animation/reader.py`
- [x] 默认返回 fcurve 摘要（`keyframe_count`, `frame_range`），不返回每个 keyframe
- [x] 添加 `keyframe_detail=true` 参数返回详细 keyframe
- [x] 添加 `max_keyframes` 截断参数

### `src/blender_mcp_addon/handlers/info/query.py`
- [x] `node_types`：添加 `max_results` 参数，默认 20
- [x] `node_types`：添加 `truncated` 标记
- [x] 移除 `reports.count` 和 `types.count`
- [ ] `version`：移除重复字段（`api_version`, `python_version_info`）
- [ ] `selection`：节点详情按需返回

### `src/blender_mcp_addon/handlers/script/executor.py`
- [x] `output` 截断到 `_MAX_OUTPUT_CHARS`（10,000）

### `src/blender_mcp_addon/handlers/operator/executor.py`
- [ ] 移除 `scopes` 字段
- [ ] `duration_ms` 移到调试日志

---

## 七、兼容性与风险

| 变更类型 | 风险 | 缓解措施 |
|---------|------|---------|
| 移除响应字段 | 依赖这些字段的客户端可能中断 | 版本化 API，或先标记为 deprecated |
| 新增 `depth` 级别 | 无破坏性 — 新增值 | 旧客户端不受影响 |
| 截断响应 | LLM 收到不完整数据 | 添加明确截断标记 |
| Schema 瘦身 | LLM 可能失去部分引导信息 | 保留关键语义，只压缩格式 |
| 移除冗余 count | 极低风险 | 数组 `.length` 始终可用 |
| 动态工具注册 | 客户端兼容性不确定 | 仅在支持的客户端启用 |

**建议**：阶段 1-2 的优化全部向后兼容（新增参数有默认值、移除的字段是冗余的），可直接实施。阶段 3 中移除 `ok`/`error` 信封需要确认 `mcp_protocol.py` 的解析逻辑同步更新。
