# Issue #167 — 独立节点组管理能力缺失：方案建议

> 日期: 2026-04-19
> Issue: https://github.com/ageless-h/blender-mcp/issues/167
> 约束: 不添加新 MCP 工具，避免架构变动引入新问题

---

## 一、问题本质

Blender MCP 当前**无法创建和管理独立节点组**（`bpy.data.node_groups`），导致以下真实场景无法实现：

| 场景 | 当前状态 | 阻塞点 |
|------|---------|--------|
| 从零构建可复用 Shader 节点组（如 43 节点的卡通材质） | ❌ 不可能 | 无法创建 ShaderNodeTree |
| 创建合成器预设节点组 | ❌ 不可能 | 无法创建 CompositorNodeTree |
| 在 Group 节点上设置 node_tree 引用 | ❌ 失败 | `coerce_value()` 不支持 NodeTree 类型 |
| 独立几何节点组（跨修改器复用） | ❌ 不可能 | 仅支持 MODIFIER 上下文绑定创建 |

**核心矛盾**: `NodeTreeHandler` 已经实现了完整的 CRUD 操作（create/read/write/delete/list/link），但没有任何 MCP 工具暴露它。代码存在但用户无法访问。

---

## 二、三种方案的深度对比

### 方案 A：添加新工具 `blender_manage_node_tree`

**Issue 中的推荐方案。**

| 维度 | 评价 |
|------|------|
| 架构影响 | ⚠️ **高** — 第 30 个 MCP 工具，增加 schema、安全管道、allowlist 条目 |
| 功能完整性 | ✅ 完整 — 独立的 CRUD 操作 |
| 与现有工具的关系 | ⚠️ **模糊** — `blender_edit_nodes` 已经可以编辑节点树内的节点，新工具负责"管理"节点树本身，职责边界不清 |
| `link()` 局限 | ⚠️ 现有 `NodeTreeHandler.link()` 仅支持 MODIFIER 目标，不支持 Material/Scene |
| 测试成本 | 高 — 需要新测试文件、CI 覆盖 |

**风险**: 引入一个新的 imperative 工具意味着修改 `schemas/tools.py`、`capabilities/imperative.py`（或 base.py）、`security/allowlist.py`、`catalog/`。链路较长，任何环节出问题都会影响现有工具。

**结论**: ❌ **不推荐** — 违反"不添加新工具"的约束，且 `NodeTreeHandler.link()` 不完整。

---

### 方案 B：扩展 `blender_edit_nodes` 增加 `NODE_GROUP` 上下文

**在现有工具上做最小扩展。**

| 维度 | 评价 |
|------|------|
| 架构影响 | ✅ **低** — 仅在现有工具的 context enum 中加一项 |
| 自然程度 | ✅ 高 — 与现有 6 个上下文（OBJECT/WORLD/LINESTYLE/SCENE/MODIFIER/TOOL）完全一致的模式 |
| 自动创建 | ✅ 复用 GEOMETRY/MODIFIER 的 auto-create 模式 |
| 缺失操作 | ⚠️ 需要新增 `add_interface_socket` 操作来管理组的输入/输出接口 |
| 测试成本 | 中等 — 扩展现有测试 |

**需要改动的文件**:
- `src/blender_mcp/schemas/tools.py` — context enum 加入 `"NODE_GROUP"`
- `src/blender_mcp_addon/handlers/nodes/reader.py` — `_resolve_node_tree` 加入 NODE_GROUP 分支
- `src/blender_mcp_addon/handlers/nodes/editor.py` — 自动创建逻辑 + `add_interface_socket` 操作

**结论**: ✅ **推荐（主方案）** — 遵循现有模式，改动集中在节点子系统内部。

---

### 方案 C：修复 `coerce_value` 支持 NodeTree 引用

**最小改动，解决 `set_property` 无法设置 `node_tree` 引用的问题。**

| 维度 | 评价 |
|------|------|
| 架构影响 | ✅ **极低** — 仅改动 `property_parser.py` 一个函数 |
| 功能完整性 | ⚠️ **不完整** — 只解决"引用"问题，不解决"创建"问题 |
| 独立价值 | ✅ 有 — 即使不做 B，也能配合 `blender_execute_operator` 实现完整流程 |
| 安全性 | 需要考虑 — 通过字符串名称查找 bpy.data 对象，但这在 Blender 中是标准模式 |

**改动范围**:
- `src/blender_mcp_addon/handlers/utils/property_parser.py` — `coerce_value()` 增加 NodeTree 类型处理

**结论**: ✅ **推荐（基础修复）** — 无论选择哪个方案，这个修复都应该做。

---

## 三、最终建议：分阶段实施 B + C

### 阶段一：修复 `coerce_value`（Option C）— 立即可做

**改动量**: ~10 行代码，1 个文件。

这是一个纯粹的 bug 修复，`coerce_value` 应该能够处理 Blender data block 引用：

```python
# property_parser.py — coerce_value() 中增加
import bpy

# 当 target 是 NodeTree（或 None 但属性名暗示引用类型），
# 尝试从 bpy.data.node_groups 解析字符串引用
if target is not None:
    target_type = type(target).__name__
    if target_type in ("NodeTree", "ShaderNodeTree", "CompositorNodeTree", 
                        "GeometryNodeTree") or (target is None and isinstance(value, str)):
        tree = bpy.data.node_groups.get(value)
        if tree is not None:
            return tree
```

**立即效果**: 以下操作将能正常工作——

```json
// 前提：先用 operator 创建节点组
{"operator": "node.new_node_tree", "params": {"name": "MyGroup", "type": "ShaderNodeTree"}}

// 现在可以在 set_property 中引用它了
{
  "tree_type": "SHADER", "context": "OBJECT", "target": "MyMaterial",
  "operations": [
    {"action": "add_node", "type": "ShaderNodeGroup", "name": "Group"},
    {"action": "set_property", "node": "Group", "property": "node_tree", "value": "MyGroup"}
  ]
}
```

**风险评估**: 极低。`coerce_value` 只在 `target` 类型匹配时才尝试查找，不影响现有的 Vector/Color/bool/float 类型处理。

---

### 阶段二：扩展 `blender_edit_nodes` 增加 `NODE_GROUP` 上下文（Option B）

**改动量**: ~60-80 行代码，3 个文件。

#### 2.1 Schema 扩展

```python
# schemas/tools.py — blender_edit_nodes 的 context enum
"context": {
    "type": "string",
    "enum": ["OBJECT", "WORLD", "LINESTYLE", "SCENE", "MODIFIER", "TOOL", 
             "NODE_GROUP"],  # ← 新增
}
```

#### 2.2 Reader 扩展

```python
# reader.py — _resolve_node_tree() 中新增分支
if context == "NODE_GROUP" and target:
    node_tree = bpy.data.node_groups.get(target)
```

#### 2.3 Editor 自动创建

```python
# editor.py — auto-create 逻辑中新增
if context == "NODE_GROUP" and target:
    node_tree = bpy.data.node_groups.get(target)
    if node_tree is None:
        # 根据 tree_type 确定 Blender 内部类型名
        type_map = {
            "SHADER": "ShaderNodeTree",
            "GEOMETRY": "GeometryNodeTree",
            "COMPOSITOR": "CompositorNodeTree",
        }
        bl_type = type_map.get(tree_type, "ShaderNodeTree")
        node_tree = bpy.data.node_groups.new(target, bl_type)
```

#### 2.4 新增操作：`add_interface_socket`

这是阶段二中**唯一真正新增的能力**。独立节点组必须通过 `interface.new_socket()` 定义输入/输出接口：

```python
# editor.py — 操作处理循环中新增
elif action == "add_interface_socket":
    socket_name = op.get("name", "Value")
    in_out = op.get("in_out", "INPUT")        # "INPUT" | "OUTPUT"
    socket_type = op.get("socket_type", "NodeSocketFloat")
    node_tree.interface.new_socket(
        name=socket_name,
        in_out=in_out,
        socket_type=socket_type,
    )
```

**完整使用流程示例**:

```json
// 步骤 1：创建 ShaderNodeTree + 定义接口 + 添加内部节点
{
  "tree_type": "SHADER",
  "context": "NODE_GROUP",
  "target": "CartoonShading",
  "operations": [
    {"action": "add_interface_socket", "name": "Base Color", "in_out": "INPUT", "socket_type": "NodeSocketColor"},
    {"action": "add_interface_socket", "name": "Roughness", "in_out": "INPUT", "socket_type": "NodeSocketFloat"},
    {"action": "add_interface_socket", "name": "Shader", "in_out": "OUTPUT", "socket_type": "NodeSocketShader"},
    {"action": "add_node", "type": "NodeGroupInput", "name": "GroupInput", "location": [-400, 0]},
    {"action": "add_node", "type": "NodeGroupOutput", "name": "GroupOutput", "location": [400, 0]},
    {"action": "add_node", "type": "ShaderNodeBsdfDiffuse", "name": "Diffuse", "location": [0, 0]},
    {"action": "connect", "from_node": "GroupInput", "from_socket": "Base Color", "to_node": "Diffuse", "to_socket": "Color"},
    {"action": "connect", "from_node": "Diffuse", "from_socket": "BSDF", "to_node": "GroupOutput", "to_socket": "Shader"}
  ]
}

// 步骤 2：在材质中使用这个节点组
{
  "tree_type": "SHADER",
  "context": "OBJECT",
  "target": "MyMaterial",
  "operations": [
    {"action": "add_node", "type": "ShaderNodeGroup", "name": "CartoonGroup"},
    {"action": "set_property", "node": "CartoonGroup", "property": "node_tree", "value": "CartoonShading"},
    {"action": "connect", "from_node": "CartoonGroup", "from_socket": "Shader", "to_node": "Material Output", "to_socket": "Surface"}
  ]
}
```

**风险评估**: 中低。改动局限在节点子系统内部（reader/editor/schema），不触及安全管道、dispatcher、handler registry。`NODE_GROUP` 上下文与现有 6 个上下文的处理模式完全一致。

---

## 四、为什么不推荐方案 A

| 原因 | 详细说明 |
|------|---------|
| 1. 违反用户约束 | 明确要求"不添加新工具" |
| 2. 架构影响面大 | 需改动 schemas → catalog → security/allowlist → capabilities/imperative → base.py dispatcher → tests |
| 3. NodeTreeHandler.link() 不完整 | 仅支持 MODIFIER 目标，不能 link 到 Material 或 Scene，需额外开发 |
| 4. 职责边界模糊 | `blender_manage_node_tree` 管理节点树生命周期，`blender_edit_nodes` 编辑节点树内部节点——但 LLM 可能混淆两个工具的使用场景 |
| 5. LLM 工具选择困难 | 29 个工具已经很多，第 30 个增加了 LLM 的选择难度，可能降低整体质量 |

---

## 五、实施优先级

```
阶段一（C）─────────────────────▶ 阶段二（B）
修复 coerce_value               扩展 blender_edit_nodes
~10 行, 1 文件                   ~60-80 行, 3 文件
立即可做                         阶段一完成后

可独立发布                       完整解决方案
配合 operator 即可创建节点组     原生支持节点组创建和编辑
```

### 阶段一的独立价值

即使不做阶段二，阶段一配合现有的 `blender_execute_operator` 已经可以实现完整工作流：

```
blender_execute_operator("node.new_node_tree", {name, type})  → 创建节点组
blender_edit_nodes(context="???")                              → 编辑内部节点 ← 仍需 operator
blender_edit_nodes(set_property, node_tree="GroupName")        → 引用节点组 ✅ (阶段一修复)
```

这不是完美方案，但已经**解除了最关键的阻塞**（无法在 Group 节点上设置 node_tree 引用）。

### 阶段二的完整价值

阶段二完成后，全部操作都通过 `blender_edit_nodes` 一个工具完成，无需借助 operator：

```
blender_edit_nodes(context="NODE_GROUP", target="MyGroup")  → 创建 + 编辑节点组
blender_edit_nodes(context="OBJECT", set_property node_tree) → 引用节点组
```

---

## 六、风险矩阵

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| coerce_value 误判非 NodeTree 属性 | 低 | 中 | 严格检查 target 类型名，仅匹配已知 NodeTree 子类 |
| NODE_GROUP 上下文破坏现有 context 逻辑 | 低 | 高 | 在 reader/editor 中独立分支处理，不修改现有 if-elif 链 |
| add_interface_socket 与 Blender 版本不兼容 | 中 | 中 | `interface.new_socket()` 是 Blender 4.0+ API，4.2 LTS 起稳定 |
| LLM 不知道何时使用 NODE_GROUP 上下文 | 中 | 低 | 更新 tool description 中的 WHEN/NOT 说明 |

---

## 七、结论

**修复 `coerce_value`（阶段一）是零风险的必做项**。它修复了一个明确的功能缺陷，不涉及任何架构变动。

**扩展 `blender_edit_nodes` 增加 `NODE_GROUP` 上下文（阶段二）是推荐的完整方案**。它复用现有架构模式，不添加新工具，改动范围可控，且完美解决 Issue 描述的所有用例。

两个阶段可以在同一个 PR 中提交，也可以分开发布。
