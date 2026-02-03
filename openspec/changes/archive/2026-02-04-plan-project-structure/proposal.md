## Why

当前仓库已有 MCP 相关代码与文档，但项目结构尚未统一规划，会影响长期维护、跨版本支持与插件端协作效率。现在需要确立清晰的目录分层与边界，保证核心服务、插件端与文档规范可以长期演进。

## What Changes

- 明确仓库顶层结构与核心目录职责（源码、插件端、文档、测试、示例、脚本）。
- 定义插件端独立目录与与核心服务的契约边界。
- 规范项目文档与设计变更的组织方式，与现有 OpenSpec 结构对齐。
- 提供目录命名与扩展原则，便于未来功能扩展与跨版本维护。

## Capabilities

### New Capabilities
- `project-structure-layout`: 顶层与核心目录结构规划与职责划分。
- `addon-directory-boundary`: 插件端独立目录与与核心服务的边界规则。
- `documentation-organization`: docs/ 与 openspec/ 的文档组织规范与入口约定。
- `code-layout-conventions`: 代码目录命名、分层与扩展规则。

### Modified Capabilities
- None.

## Impact

- 仓库目录树与规范文件将新增或调整。
- 开发与维护流程将依赖统一的目录约定与文档入口。
