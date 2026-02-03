## 1. 目录结构方案

- [x] 1.1 定义仓库顶层目录清单与职责（src/, addon/, docs/, tests/, examples/, scripts/）
- [x] 1.2 定义核心包根路径与命名规则（与仓库名一致的小写包名）
- [x] 1.3 定义模块分层规则（core/transport/adapters/security/catalog/versioning/validation）

## 2. 插件端边界

- [x] 2.1 规划插件端独立目录结构与入口文件布局
- [x] 2.2 定义插件端契约文档模板（入口点、版本、兼容策略）

## 3. 文档与规范组织

- [x] 3.1 制作文档目录树规范（docs/ 按领域分组）
- [x] 3.2 明确 OpenSpec 工件位置与引用方式（openspec/changes/）

## 4. 协议与传输方案约束

- [x] 4.1 记录协议选择与 SDK 版本策略（官方 MCP 协议与 SDK）
- [x] 4.2 明确 MVP 传输方案与后续扩展位（stdio → HTTP/WebSocket）

## 5. 安全性风险分析

- [x] 5.1 识别插件端与核心服务边界的安全风险与隔离策略
- [x] 5.2 评估传输层风险（stdio/网络传输）与最小化暴露面
- [x] 5.3 评估依赖与版本演进风险（SDK/Blender 版本）
