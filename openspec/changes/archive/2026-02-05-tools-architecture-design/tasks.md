## 1. 基础设施

- [x] 1.1 创建 DataType 枚举定义 (`src/blender_mcp_addon/handlers/types.py`)
- [x] 1.2 实现 BaseHandler 抽象基类 (`src/blender_mcp_addon/handlers/base.py`)
- [x] 1.3 实现 HandlerRegistry 注册器 (`src/blender_mcp_addon/handlers/registry.py`)
- [x] 1.4 实现统一的响应格式工具函数 (`_ok`, `_error`)

## 2. 数据层工具 (data.*)

- [x] 2.1 实现 ObjectHandler (object 类型 CRUD)
- [x] 2.2 实现 MeshHandler (mesh 类型 CRUD)
- [x] 2.3 实现 MaterialHandler (material 类型 CRUD)
- [x] 2.4 实现 CollectionHandler (collection 类型 CRUD)
- [x] 2.5 实现 SceneHandler (scene 类型 CRUD)
- [x] 2.6 实现 NodeTreeHandler (node_tree 类型 CRUD)
- [x] 2.7 实现 ImageHandler (image 类型 CRUD，含 base64 支持)
- [x] 2.8 实现 ContextHandler (context 伪类型读写)
- [x] 2.9 实现 ModifierHandler (modifier 附属类型)
- [x] 2.10 实现其他核心 Handler (camera, light, armature, curve, world)
- [x] 2.11 实现 data.link 关联逻辑

## 3. 操作层工具 (operator.execute)

- [x] 3.1 实现 operator.execute 基础框架
- [x] 3.2 实现上下文覆盖逻辑 (使用 temp_override)
- [x] 3.3 实现操作符结果捕获 (reports, result status)
- [x] 3.4 实现 scope 映射 (operator 到 required scopes)

## 4. 信息层工具 (info.query)

- [x] 4.1 实现 info.query 基础框架和 InfoType 枚举
- [x] 4.2 实现 reports 查询类型
- [x] 4.3 实现 last_op 查询类型
- [x] 4.4 实现 undo_history 查询类型
- [x] 4.5 实现 scene_stats 查询类型
- [x] 4.6 实现 selection 查询类型
- [x] 4.7 实现 mode 查询类型
- [x] 4.8 实现 changes 查询类型 (变更追踪)
- [x] 4.9 实现 viewport_capture 查询类型 (base64 截图)
- [x] 4.10 实现 version 和 memory 查询类型

## 5. 可选工具 (script.execute)

- [x] 5.1 实现 script.execute 基础框架
- [x] 5.2 实现执行超时控制
- [x] 5.3 实现返回值和输出捕获
- [x] 5.4 添加默认禁用配置和启用检查
- [x] 5.5 集成 audit logging

## 6. 能力调度器重构

- [x] 6.1 重构 execute_capability 使用 HandlerRegistry
- [x] 6.2 移除旧的 scene.read/scene.write 硬编码
- [x] 6.3 更新能力路由逻辑支持新工具名称

## 7. 能力目录更新

- [x] 7.1 更新 minimal_capability_set() 返回新工具元数据
- [x] 7.2 更新 CapabilityMeta 结构支持新工具
- [x] 7.3 更新 scope 映射 (capability_scope_map)

## 8. 安全层集成

- [x] 8.1 更新 allowlist 支持新工具名称
- [x] 8.2 添加 script.execute 的特殊安全控制
- [x] 8.3 验证 rate-limit 与新工具兼容

## 9. 测试

- [x] 9.1 为每个 Handler 编写单元测试
- [x] 9.2 为 operator.execute 编写上下文覆盖测试
- [x] 9.3 为 info.query 编写各类型测试
- [x] 9.4 为 script.execute 编写安全测试
- [x] 9.5 更新集成测试 (test_workflows.py)

## 10. 迁移与文档

- [x] 10.1 创建迁移指南 (scene.read → data.read)
- [x] 10.2 更新 README 工具说明
- [x] 10.3 验证 docs/tools/ 文档与实现一致

