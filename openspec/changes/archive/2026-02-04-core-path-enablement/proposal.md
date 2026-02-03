## Why

当前代码存在同时使用根目录包与 src 布局的可能，导致安装与导入路径不一致，影响可维护性与发布稳定性。需要明确单一代码根并补齐打包配置，避免依赖和导入混乱。

## What Changes

- 明确代码根路径选择（`src/blender_mcp/` 或根目录 `blender_mcp/`）并给出迁移策略。
- 补齐 `pyproject.toml` 的打包与安装配置，确保可正常安装与导入。
- 明确包发现规则与入口点，避免多根路径冲突。

## Capabilities

### New Capabilities
- `code-root-decision`: 代码根路径选择与迁移策略的规范。
- `packaging-configuration`: `pyproject.toml` 的打包与安装配置规范。
- `validation-gate-ci`: 测试对齐与最小 CI 门槛规范。

### Modified Capabilities
- None.

## Impact

- 代码布局与导入路径将被统一。
- 构建与安装流程将依赖新的打包配置。
- 测试与 CI 将作为基础门槛纳入工程流程。
