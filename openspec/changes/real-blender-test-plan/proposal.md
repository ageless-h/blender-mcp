## Why

当前项目的集成测试基于 `MockAdapter`，无法验证与真实 Blender 的交互行为。为确保 blender-mcp 在支持的 Blender 版本（4.2 LTS、4.5 LTS、5.0+）上正常工作，需要建立针对真实 Blender 可执行文件的端到端测试能力。用户已部署三个目标版本，需立即启用真实环境测试。

## What Changes

- 新增本地 Blender 路径配置机制，支持指定多个 Blender 可执行文件路径
- 新增真实 Blender 测试 harness，能够启动 Blender 进程、注入测试脚本、通过 socket 通信
- 新增针对真实 Blender 的集成测试套件，覆盖核心 capability 执行路径
- 新增多版本测试执行器，按配置的 Blender 版本矩阵运行测试并汇总结果
- 更新 `compatibility-results.json` 填充真实测试数据

## Capabilities

### New Capabilities

- `real-blender-test-harness`: 提供启动真实 Blender 进程、建立 socket 通信、执行测试脚本的基础设施
- `blender-path-configuration`: 支持配置和发现本地 Blender 可执行文件路径，按版本组织

### Modified Capabilities

- `integration-tests-and-examples`: 扩展现有集成测试规范，增加针对真实 Blender 的测试场景要求

## Impact

### 代码影响
- `tests/integration/`: 新增真实 Blender 测试模块和 harness
- `scripts/`: 新增多版本测试执行脚本
- `docs/versioning/compatibility-results.json`: 更新测试结果数据

### 配置影响
- 需要新增测试配置文件存储 Blender 路径（如 `tests/blender-paths.json` 或环境变量）

### 依赖影响
- 测试执行依赖本地安装的 Blender（非运行时依赖）

### 目标 Blender 版本
| 版本 | 路径 | 状态 |
|------|------|------|
| 4.2.17 LTS | `F:\Program Files\blender\LTS\blender-4.2.17-windows-x64\blender.exe` | baseline |
| 4.5.6 LTS | `F:\Program Files\blender\LTS\blender-4.5.6-windows-x64\blender.exe` | latest LTS |
| 5.0.1 | `F:\Program Files\blender\blender-5.0.1-windows-x64\blender.exe` | current stable |

