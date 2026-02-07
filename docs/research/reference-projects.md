# Reference Projects Review

> **更新日期**: 2026-02-07  
> **研究范围**: Blender MCP、Unity MCP、3D 工具 MCP 实现

---

## 核心竞品分析

### ahujasid/blender-mcp ⭐ 16,903

**仓库**: https://github.com/ahujasid/blender-mcp

**概述**:
- 最流行的 Blender MCP 实现
- 22 个高层工具
- 1,185 行服务器代码
- FastMCP + 装饰器架构

**工具列表**:
| 工具 | 用途 |
|------|------|
| `get_scene_info` | 获取场景信息 |
| `get_object_info` | 获取对象详情 |
| `get_viewport_screenshot` | 视口截图 |
| `execute_blender_code` | 执行 Python 代码（逃生舱） |
| `get_polyhaven_*` | PolyHaven 集成 |
| `search/download_sketchfab_*` | Sketchfab 集成 |
| `generate_hyper3d_*` | Hyper3D AI 生成 |
| `generate_hunyuan3d_*` | Hunyuan3D AI 生成 |

**成功因素**:
1. **高层抽象**: 不是 `create_cube`，而是 `download_polyhaven_asset`
2. **外部集成**: PolyHaven、Sketchfab、Hyper3D、Hunyuan3D
3. **逃生舱**: `execute_blender_code` 允许执行任意 Python
4. **Prompt 引导**: `@mcp.prompt()` 函数指导 AI 工作流
5. **遥测支持**: `@telemetry_tool` 装饰器

**可借鉴**:
- 外部资产集成模式
- Prompt 引导工作流
- 逃生舱设计

---

### CoplayDev/unity-mcp ⭐ 5,693

**仓库**: https://github.com/CoplayDev/unity-mcp

**概述**:
- 最成熟的 3D 工具 MCP 实现
- 22 个领域驱动工具
- `manage_*` 命名模式
- 支持多 Unity 实例

**工具列表**:
| 工具 | 用途 |
|------|------|
| `manage_asset` | 资产管理（导入、创建、修改、删除） |
| `manage_editor` | 编辑器控制 |
| `manage_gameobject` | 游戏对象管理 |
| `manage_material` | 材质管理 |
| `manage_prefabs` | 预制体管理 |
| `manage_scene` | 场景管理 |
| `manage_script` | 脚本管理 |
| `batch_execute` | 批量执行（10-100x 性能提升） |

**成功因素**:
1. **领域驱动**: `manage_*` 模式，一个工具管理一个领域
2. **批量操作**: `batch_execute` 显著提升性能
3. **多实例支持**: 可管理多个 Unity Editor
4. **详细的参数描述**: 每个参数都有清晰的说明

**可借鉴**:
- `manage_*` 命名模式
- `batch_execute` 批量操作
- 领域驱动的工具组织

---

### llm-use/Blender-MCP-Server

**仓库**: https://github.com/llm-use/Blender-MCP-Server

**概述**:
- 51 个细粒度工具
- 5,605 行单文件代码
- PolyMCP 框架
- 线程安全执行

**问题**:
- ❌ 单文件巨无霸（5,605 行）
- ❌ 工具选择困难（AI 要在 51 个工具中选择）
- ❌ 维护成本高
- ❌ 上下文管理复杂

**教训**:
- 更多工具 ≠ 更好的效果
- 避免单文件巨无霸
- 工具数量应控制在 20-30 个

---

### basementstudio/mcp-three

**仓库**: https://github.com/basementstudio/mcp-three

**概述**:
- Three.js MCP 实现
- TypeScript 架构
- 单文件单工具模式
- 清晰的 schema 和 metadata

**架构特点**:
```typescript
// src/tools/get-model-structure.ts
export const schema = {
  modelPath: z.string().describe("The path to GLTF/GLB model file...")
}

export const metadata = {
  name: "get-model-structure",
  description: "Get structure of a GLTF/GLB model file...",
  annotations: {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
  },
}
```

**可借鉴**:
- 单文件单工具的模块化组织
- 明确的 schema 和 metadata
- 注解驱动（readOnlyHint、destructiveHint）

---

### chrome-devtools-mcp

**概述**:
- 强调稳定的工具注册表和严格的请求路由
- 清晰分离协议处理和平台特定适配器
- 提供能力目录组织和审计模型

**可借鉴**:
- 适配器边界模式
- 工具注册表结构
- 审计日志设计

---

## 工具数量对比

| 项目 | Stars | 工具数量 | 代码行数 | 架构风格 |
|------|-------|----------|----------|----------|
| ahujasid/blender-mcp | 16,903 | 22 | 1,185 | 高层抽象 |
| Unity MCP | 5,693 | 22 | - | 领域驱动 |
| llm-use/Blender-MCP | - | 51 | 5,605 | 细粒度 |
| mcp-three | - | ~5 | - | 模块化 |
| **本项目** | - | **8** | - | **统一 CRUD** |

**结论**: 行业领先者采用 **20-30 个高层工具**，本项目的 8 工具架构方向正确。

---

## 适用于 Blender MCP 的建议

### 从 ahujasid/blender-mcp 学习
- [ ] 添加 `@mcp.prompt()` 工作流指南
- [ ] 考虑外部集成（PolyHaven、Sketchfab）
- [ ] 启用 `script.execute` 逃生舱

### 从 Unity MCP 学习
- [ ] 添加 `batch_execute` 批量操作
- [ ] 改进参数描述的详细程度
- [ ] 考虑 `manage_*` 命名模式

### 从 mcp-three 学习
- [ ] 模块化代码组织
- [ ] 添加工具注解（readOnlyHint 等）

### 避免 llm-use 的问题
- [ ] 不要创建过多细粒度工具
- [ ] 避免单文件巨无霸
- [ ] 保持工具数量在 20-30 个以内

---

## 参考链接

- [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp)
- [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp)
- [llm-use/Blender-MCP-Server](https://github.com/llm-use/Blender-MCP-Server)
- [basementstudio/mcp-three](https://github.com/basementstudio/mcp-three)
