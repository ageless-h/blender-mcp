## Why

Blender Python API 包含 1000+ 个操作符和数十种数据类型。为每个操作创建独立的 MCP 工具会导致开发成本极高、维护困难、AI 难以理解。需要一种高度压缩但功能完整的工具架构设计，通过统一接口覆盖 99.9% 的 Blender 功能。

## What Changes

- **新增统一数据层工具**：6 个 `data.*` 工具替代数百个数据操作工具，通过 `DataType` 参数化覆盖所有 `bpy.data.*` 操作
- **新增通用操作执行器**：1 个 `operator.execute` 工具替代 1000+ 个 `bpy.ops.*` 封装，支持上下文覆盖
- **新增信息查询工具**：1 个 `info.query` 工具提供操作反馈、历史记录、场景统计、视口截图等 LLM 必需的元信息
- **新增可选危险工具**：1 个 `script.execute` 工具（默认禁用）作为逃生舱覆盖边缘情况
- **新增数据类型枚举**：定义 30+ 种 `DataType`，映射 Blender 所有数据块类型
- **BREAKING**：替换现有的 `scene.read` / `scene.write` 能力为新的统一工具架构

## Capabilities

### New Capabilities

- `unified-data-crud`: 统一数据 CRUD 工具集（data.create/read/write/delete/list/link），通过类型参数化覆盖所有 bpy.data 操作
- `operator-execution`: 通用操作执行工具（operator.execute），支持上下文覆盖，覆盖所有 bpy.ops 操作
- `info-query`: 信息查询工具（info.query），提供操作反馈、历史、统计、截图等 LLM 必需的元信息
- `unsafe-script-execution`: 可选的危险脚本执行工具（script.execute），默认禁用，需要显式启用
- `blender-data-types`: Blender 数据类型枚举定义，映射 30+ 种 bpy.data 数据块类型

### Modified Capabilities

- `minimum-capability-set`: 现有最小能力集将被新的工具架构替代，需要更新能力注册和 scope 映射

## Impact

- **代码影响**：
  - `src/blender_mcp_addon/capabilities/` - 重构为新的工具架构
  - `src/blender_mcp/catalog/` - 更新能力目录和元数据
  - `src/blender_mcp/security/` - 新增 `script.execute` 的安全控制
  
- **API 变更**：
  - 工具名称从 `scene.read`/`scene.write` 变更为 `data.read`/`data.write` 等
  - 新增 `type` 参数用于指定数据类型
  - 新增 `context` 参数用于操作符上下文覆盖
  
- **依赖**：
  - 无新增外部依赖
  - 依赖现有的安全层（allowlist、rate-limit、audit-logging）
  
- **文档**：
  - 已创建 `docs/tools/` 文档集，包含完整的工具设计文档

