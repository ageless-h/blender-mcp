# -*- coding: utf-8 -*-
# MCP 工具设计研究发现与实施建议

> **研究日期**: 2026-02-07  
> **研究范围**: MCP 官方文档、行业最佳实践、竞品分析  
> **核心问题**: 8 工具架构是否正确？LLM 为何不理解参数？如何优化？

---

## 执行摘要

### 核心结论

| 问题 | 结论 |
|------|------|
| 8 工具架构方向是否正确？ | ✅ **正确**，与行业领先者一致 |
| 为什么 LLM 不理解参数？ | ❌ **inputSchema 过于简单**，缺少 enum 约束和详细描述 |
| 应该继续还是调转方向？ | ✅ **继续**，但需要改进参数设计 |

### 关键洞察

> **"MCP 是 AI 的用户界面，不是 API 包装器。"**  
> — [Anthropic 官方工具设计指南](https://www.anthropic.com/engineering/writing-tools-for-agents)

你的问题不是"工具数量太少"，而是"工具的参数描述不够 LLM 友好"。

---

## 第一部分：行业基准分析

### 1.1 竞品工具数量对比

| 项目 | Stars | 工具数量 | 代码行数 | 架构风格 |
|------|-------|----------|----------|----------|
| **ahujasid/blender-mcp** | 16,903 ⭐ | 22 工具 | 1,185 行 | 高层抽象 + 外部集成 |
| **Unity MCP (CoplayDev)** | 5,693 ⭐ | 22 工具 | - | 领域驱动 (`manage_*`) |
| **llm-use/Blender-MCP-Server** | - | 51 工具 | 5,605 行 | 细粒度操作 |
| **你的项目** | - | 8 工具 | - | 统一 CRUD |

**发现**: 行业领先者（ahujasid、Unity MCP）都采用 **20-30 个高层工具**，而不是 hundreds of primitives。

### 1.2 成功项目的共同特征

#### ahujasid/blender-mcp（最流行，16.9k stars）

**工具列表**:
```
get_scene_info          获取场景信息
get_object_info         获取对象详情
get_viewport_screenshot 视口截图
execute_blender_code    执行 Python 代码（逃生舱）
get_polyhaven_*         PolyHaven 集成（HDRI、纹理、模型）
search/download_sketchfab_* Sketchfab 集成
generate_hyper3d_*      Hyper3D AI 生成
generate_hunyuan3d_*    Hunyuan3D AI 生成
set_texture             应用纹理
```

**成功因素**:
1. **高层抽象**: 不是 `create_cube`，而是 `download_polyhaven_asset`
2. **外部集成**: PolyHaven、Sketchfab、Hyper3D、Hunyuan3D
3. **逃生舱**: `execute_blender_code` 允许执行任意 Python
4. **Prompt 引导**: `@mcp.prompt()` 函数指导 AI 工作流
5. **遥测支持**: `@telemetry_tool` 装饰器

#### Unity MCP（最成熟的 3D 工具 MCP）

**工具列表**:
```
manage_asset            资产管理（导入、创建、修改、删除）
manage_editor           编辑器控制
manage_gameobject       游戏对象管理
manage_material         材质管理
manage_prefabs          预制体管理
manage_scene            场景管理
manage_script           脚本管理
batch_execute           批量执行（10-100x 性能提升）
...
```

**成功因素**:
1. **领域驱动**: `manage_*` 模式，一个工具管理一个领域
2. **批量操作**: `batch_execute` 显著提升性能
3. **多实例支持**: 可管理多个 Unity Editor
4. **详细的参数描述**: 每个参数都有清晰的说明

### 1.3 失败模式分析

#### llm-use/Blender-MCP-Server（51 工具，5,605 行）

**问题**:
- ❌ 单文件巨无霸（5,605 行）
- ❌ 工具选择困难（AI 要在 51 个工具中选择）
- ❌ 维护成本高
- ❌ 上下文管理复杂

**教训**: 更多工具 ≠ 更好的效果

---

## 第二部分：MCP 工具设计最佳实践

### 2.1 官方指南核心原则

来源: [Anthropic - Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)

#### 原则 1: 面向结果，而非操作

```python
# ❌ 错误: 三个分离的工具，需要 3 次往返
def get_user_by_email(email: str) -> dict
def list_orders(user_id: str) -> list
def get_order_status(order_id: str) -> dict

# ✅ 正确: 一个高级工具，内部完成编排
def track_latest_order(email: str) -> dict:
    """获取指定邮箱的最新订单状态"""
    # 内部调用多个 API，代理只需一次调用
```

#### 原则 2: 展平参数

```python
# ❌ 错误: 复杂的嵌套字典
def search_orders(filters: dict) -> list:
    # AI: 这字典里应该有哪些键？

# ✅ 正确: 顶层基本类型 + 约束
def search_orders(
    email: str,
    status: Literal["pending", "shipped", "delivered"] = "pending",
    limit: int = 10
) -> list:
    """搜索订单，支持状态过滤"""
```

#### 原则 3: 指令即上下文

```python
# ❌ 错误: 空文档字符串
def create_issue() -> dict:
    pass

# ✅ 正确: 详细的使用指导
def create_issue(title: str, description: str) -> dict:
    """
    在项目中创建新问题
    
    使用时机: 当用户要求报告 bug 或功能请求时
    
    参数说明:
        - title: 问题标题（1-100 字符）
        - description: 详细描述
        
    返回:
        issue_id: 创建的问题 ID
        url: 问题 URL
    """
```

#### 原则 4: 严格筛选工具

- 每个服务器 **5-15 个工具**
- 每个服务器 **一个职责**
- 删除未使用的工具
- 按角色划分（admin/user）

#### 原则 5: 为发现而命名

```python
# ❌ 错误: 通用名称导致冲突
create_issue  # GitHub MCP 和 Jira MCP 都有

# ✅ 正确: 服务前缀
github_create_issue()
jira_create_issue()
blender_create_object()
```

#### 原则 6: 分页大数据集

```python
def list_objects(
    limit: int = 50,
    offset: int = 0
) -> dict:
    """
    返回:
        {
            "items": [...],
            "has_more": True/False,
            "next_offset": 100,
            "total_count": 250
        }
    """
```

### 2.2 六工具模式

来源: [MCP Bundles - Tool Design Pattern](https://www.mcpbundles.com/blog/mcp-tool-design-pattern/)

避免"上下文腐烂"（Context Rot）的平衡模式：

| 类别 | 工具 | 用途 |
|------|------|------|
| **通用接口** | `fetch` | 通过 ID 获取特定资源 |
| **通用接口** | `search` | 查找匹配的资源 |
| **丰富列表** | `list_collections` | 显示可用数据 |
| **丰富列表** | `list_objects` | 浏览实际数据 |
| **写操作** | `create_object` | 创建资源 |
| **写操作** | `update_object` | 更新/删除资源 |

**关键**: 6 个参数丰富的工具 < 60 个简单工具

### 2.3 参数设计最佳实践

#### 使用 Enum 约束选择

```json
{
  "object_type": {
    "type": "string",
    "enum": ["cube", "sphere", "cylinder", "cone", "torus"],
    "description": "要创建的几何体类型"
  }
}
```

#### 提供默认值

```json
{
  "size": {
    "type": "number",
    "default": 1.0,
    "minimum": 0.01,
    "maximum": 100.0,
    "description": "对象大小（米）"
  }
}
```

#### 详细的参数描述

```python
# ❌ 不好的描述
"include_schema": "包含完整架构"

# ✅ 好的描述 - 教授 AI 何时使用
"include_schema": """
    包含每个集合的完整架构定义（属性、数据类型、
    向量化器配置）。当你在查询之前需要了解结构时
    设置为 true。默认: false
"""
```

---

## 第三部分：问题诊断

### 3.1 当前架构的问题

#### 问题 1: inputSchema 过于简单

**当前实现** (`mcp_protocol.py`):
```python
inputSchema={
    "type": "object",
    "properties": {
        "payload": {
            "type": "object",
            "description": f"Parameters for {cap.name}"  # ← 太模糊！
        }
    },
    "required": ["payload"]
}
```

**问题**: LLM 只看到 "payload 是一个 object"，完全不知道里面应该有什么。

#### 问题 2: 缺少 Enum 约束

**当前**:
```json
{
  "type": "object",
  "params": {"object_type": "MESH"}
}
```

**问题**: LLM 不知道 `object_type` 有哪些有效值。

#### 问题 3: 嵌套结构过深

**当前**:
```json
{
  "payload": {
    "type": "object",
    "name": "MyCube",
    "params": {
      "object_type": "MESH",
      "location": [0, 0, 0]
    }
  }
}
```

**问题**: 三层嵌套（payload → params → 具体参数），LLM 容易迷失。

### 3.2 与成功项目的对比

| 方面 | ahujasid/blender-mcp | 你的项目 |
|------|---------------------|----------|
| 参数风格 | 展平的顶层参数 | 嵌套的 payload 对象 |
| 类型约束 | `Literal["cube", "sphere"]` | 无约束的字符串 |
| 默认值 | 大量默认值 | 较少默认值 |
| 文档字符串 | 详细的使用指导 | 简单的描述 |
| 逃生舱 | `execute_blender_code` | `script.execute`（默认禁用） |

---

## 第四部分：实施建议

### 4.1 优先级排序

| 优先级 | 任务 | 预期效果 | 工作量 |
|--------|------|----------|--------|
| **P0** | 改进 inputSchema | LLM 立即理解参数 | 中 |
| **P0** | 添加 Prompt 引导 | 减少 LLM 猜测 | 低 |
| **P1** | 启用 script.execute | 提供逃生舱 | 低 |
| **P1** | 添加 batch_execute | 10-100x 性能提升 | 中 |
| **P2** | 外部集成（PolyHaven） | 增加实用性 | 高 |
| **P3** | 拆分部分工具 | 更直观的工具名 | 高 |

### 4.2 P0: 改进 inputSchema

#### 改造前

```python
# mcp_protocol.py
inputSchema={
    "type": "object",
    "properties": {
        "payload": {
            "type": "object",
            "description": f"Parameters for {cap.name}"
        }
    },
    "required": ["payload"]
}
```

#### 改造后

为每个工具定义详细的 schema：

```python
# schemas/data_create.py
DATA_CREATE_SCHEMA = {
    "type": "object",
    "properties": {
        "data_type": {
            "type": "string",
            "enum": [
                "object", "mesh", "material", "collection", 
                "light", "camera", "curve", "armature"
            ],
            "description": "要创建的 Blender 数据块类型"
        },
        "name": {
            "type": "string",
            "description": "数据块名称（最多 63 字符）",
            "maxLength": 63
        },
        "object_type": {
            "type": "string",
            "enum": [
                "MESH", "CURVE", "SURFACE", "META", "FONT", 
                "ARMATURE", "LATTICE", "EMPTY", "CAMERA", "LIGHT"
            ],
            "description": "对象类型（仅当 data_type='object' 时需要）"
        },
        "mesh_type": {
            "type": "string",
            "enum": [
                "CUBE", "SPHERE", "CYLINDER", "CONE", "TORUS", 
                "PLANE", "CIRCLE", "GRID", "MONKEY"
            ],
            "description": "网格几何体类型（仅当创建网格对象时需要）"
        },
        "location": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "default": [0, 0, 0],
            "description": "3D 位置 [x, y, z]"
        },
        "rotation": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "default": [0, 0, 0],
            "description": "欧拉旋转 [x, y, z]（弧度）"
        },
        "scale": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 3,
            "maxItems": 3,
            "default": [1, 1, 1],
            "description": "缩放 [x, y, z]"
        }
    },
    "required": ["data_type", "name"],
    "additionalProperties": false
}
```

### 4.3 P0: 添加 Prompt 引导

```python
# mcp_protocol.py
@mcp.prompt()
def blender_workflow_guide() -> str:
    """Guides AI on how to use Blender MCP tools effectively"""
    return """
## Blender MCP 工具使用指南

### 工具概览
- `data.create` - 创建数据块（对象、材质、集合等）
- `data.read` - 读取数据块属性
- `data.write` - 修改数据块属性
- `data.delete` - 删除数据块
- `data.list` - 列出数据块
- `data.link` - 关联数据块
- `operator.execute` - 执行 Blender 操作符
- `info.query` - 查询场景信息

### 常见工作流

#### 创建一个立方体
```json
{
  "tool": "data.create",
  "data_type": "object",
  "name": "MyCube",
  "object_type": "MESH",
  "mesh_type": "CUBE",
  "location": [0, 0, 0]
}
```

#### 移动对象
```json
{
  "tool": "data.write",
  "data_type": "object",
  "name": "MyCube",
  "location": [1, 2, 3]
}
```

#### 添加细分修改器
```json
{
  "tool": "operator.execute",
  "operator": "object.modifier_add",
  "params": {"type": "SUBSURF"}
}
```

### 数据类型参考

| data_type | 说明 | 常用参数 |
|-----------|------|----------|
| object | 场景对象 | object_type, location, rotation, scale |
| mesh | 网格数据 | vertices, edges, faces |
| material | 材质 | use_nodes, diffuse_color |
| collection | 集合 | - |
| light | 灯光 | light_type, energy, color |
| camera | 相机 | lens, clip_start, clip_end |

### 最佳实践
1. 先用 `info.query` 了解当前场景状态
2. 创建对象时总是指定 `name`
3. 使用 `data.list` 查找已有对象
4. 复杂操作使用 `operator.execute`
"""
```

### 4.4 P1: 启用 script.execute 逃生舱

```python
# 在配置中添加选项
ENABLE_SCRIPT_EXECUTE = os.getenv("BLENDER_MCP_ENABLE_SCRIPT", "false").lower() == "true"

@mcp.tool()
def script_execute(ctx: Context, code: str) -> str:
    """
    执行任意 Python 代码（需要显式启用）
    
    ⚠️ 安全警告: 此工具可以执行任意代码，仅在受信任环境中使用。
    
    使用时机:
    - 当其他工具无法完成任务时
    - 需要执行复杂的 Blender 操作时
    - 调试和实验时
    
    Parameters:
    - code: 要执行的 Python 代码（可以使用 bpy 模块）
    
    示例:
    ```python
    import bpy
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    cube = bpy.context.object
    cube.name = "MyCube"
    result = {"name": cube.name, "location": list(cube.location)}
    ```
    """
    if not ENABLE_SCRIPT_EXECUTE:
        return {"error": "script.execute is disabled. Set BLENDER_MCP_ENABLE_SCRIPT=true to enable."}
    
    # 执行代码...
```

### 4.5 P1: 添加 batch_execute

参考 Unity MCP 的实现：

```python
@mcp.tool()
def batch_execute(
    ctx: Context,
    commands: list[dict]
) -> dict:
    """
    批量执行多个 Blender 操作（10-100x 性能提升）
    
    使用时机:
    - 需要创建多个对象时
    - 需要执行一系列相关操作时
    - 性能敏感的场景
    
    Parameters:
    - commands: 命令列表，每个命令包含 tool 和参数
    
    示例:
    ```json
    {
      "commands": [
        {"tool": "data.create", "data_type": "object", "name": "Cube1", "mesh_type": "CUBE"},
        {"tool": "data.create", "data_type": "object", "name": "Cube2", "mesh_type": "CUBE"},
        {"tool": "data.write", "data_type": "object", "name": "Cube1", "location": [1, 0, 0]},
        {"tool": "data.write", "data_type": "object", "name": "Cube2", "location": [-1, 0, 0]}
      ]
    }
    ```
    
    Returns:
        {
            "success": true,
            "results": [...],
            "execution_time_ms": 45
        }
    """
```

### 4.6 P2: 外部集成（可选）

参考 ahujasid/blender-mcp 的成功模式：

```python
# 可选的外部集成
@mcp.tool()
def search_polyhaven_assets(
    ctx: Context,
    asset_type: Literal["hdris", "textures", "models"] = "all",
    categories: str = None,
    limit: int = 20
) -> str:
    """
    搜索 PolyHaven 资产（HDRI、纹理、模型）
    
    PolyHaven 提供高质量的免费 CC0 资产。
    """

@mcp.tool()
def download_polyhaven_asset(
    ctx: Context,
    asset_id: str,
    asset_type: Literal["hdris", "textures", "models"],
    resolution: Literal["1k", "2k", "4k"] = "1k"
) -> str:
    """
    下载并导入 PolyHaven 资产到 Blender
    """
```

---

## 第五部分：实施路线图

### 阶段 1: 快速修复（1-2 天）

- [ ] 为每个工具定义详细的 inputSchema
- [ ] 添加 `@mcp.prompt()` 工作流指南
- [ ] 改进工具描述文档

### 阶段 2: 功能增强（3-5 天）

- [ ] 启用 `script.execute` 逃生舱（带安全警告）
- [ ] 添加 `batch_execute` 批量操作
- [ ] 添加更多 Enum 约束

### 阶段 3: 外部集成（可选，1-2 周）

- [ ] PolyHaven 集成（HDRI、纹理、模型）
- [ ] Sketchfab 集成（模型搜索和导入）
- [ ] AI 生成集成（Hyper3D、Hunyuan3D）

### 阶段 4: 优化和测试（持续）

- [ ] 收集 LLM 使用反馈
- [ ] 优化参数描述
- [ ] 添加更多使用示例

---

## 第六部分：评估指标

### 成功标准

| 指标 | 当前 | 目标 |
|------|------|------|
| LLM 首次调用成功率 | ~30% | >80% |
| 平均完成任务的工具调用次数 | 5-10 | 2-3 |
| 参数错误率 | 高 | <10% |
| 用户满意度 | 低 | 高 |

### 测试方法

1. **单元测试**: 验证 schema 正确性
2. **集成测试**: 验证工具执行正确性
3. **LLM 测试**: 使用多个 LLM 测试工具理解度
4. **用户测试**: 收集真实用户反馈

---

## 附录

### A. 参考资源

1. [Anthropic - Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
2. [Phil Schmid - MCP Best Practices](https://www.philschmid.de/mcp-best-practices/)
3. [MCP Bundles - Six Tool Pattern](https://www.mcpbundles.com/blog/mcp-tool-design-pattern/)
4. [Redpanda - MCP Server Best Practices](https://docs.redpanda.com/redpanda-connect/ai-agents/mcp-server/best-practices/)
5. [MCP Best Practice Guide](https://mcp-best-practice.github.io/mcp-best-practice/best-practice/)

### B. 竞品仓库

1. [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) - 16.9k stars
2. [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp) - 5.7k stars
3. [llm-use/Blender-MCP-Server](https://github.com/llm-use/Blender-MCP-Server)
4. [basementstudio/mcp-three](https://github.com/basementstudio/mcp-three)

### C. 关键代码示例

#### 完整的 inputSchema 示例

```json
{
  "name": "blender_data_create",
  "description": "在 Blender 中创建数据块（对象、材质、集合等）",
  "inputSchema": {
    "type": "object",
    "properties": {
      "data_type": {
        "type": "string",
        "enum": ["object", "mesh", "material", "collection", "light", "camera"],
        "description": "要创建的数据块类型"
      },
      "name": {
        "type": "string",
        "description": "数据块名称",
        "maxLength": 63
      },
      "object_type": {
        "type": "string",
        "enum": ["MESH", "CURVE", "EMPTY", "CAMERA", "LIGHT"],
        "description": "对象类型（仅当 data_type='object' 时）"
      },
      "mesh_type": {
        "type": "string",
        "enum": ["CUBE", "SPHERE", "CYLINDER", "CONE", "TORUS", "PLANE"],
        "description": "网格类型（仅当创建网格对象时）"
      },
      "location": {
        "type": "array",
        "items": {"type": "number"},
        "minItems": 3,
        "maxItems": 3,
        "default": [0, 0, 0],
        "description": "3D 位置 [x, y, z]"
      }
    },
    "required": ["data_type", "name"]
  }
}
```

---

## 变更历史

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-02-07 | 1.0 | 初始版本 |
