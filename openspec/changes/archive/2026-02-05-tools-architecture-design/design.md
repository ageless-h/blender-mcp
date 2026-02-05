## Context

当前 Blender MCP 实现了最小能力集（`scene.read`、`scene.write`），采用细粒度的能力命名（如 `object.transform.write`）。这种方式在扩展到完整 Blender API 时会产生 1000+ 个工具，导致：
- 开发成本极高：每个操作都需要单独实现
- AI 理解困难：工具列表过长，选择困难
- 维护负担重：API 变更需要更新大量工具

现有代码结构：
- `src/blender_mcp_addon/capabilities/base.py` - 能力调度器（字符串匹配）
- `src/blender_mcp_addon/capabilities/scene.py` - 场景能力实现
- `src/blender_mcp/catalog/catalog.py` - 能力元数据注册

约束：
- 必须与现有安全层（allowlist、rate-limit、permissions）集成
- 必须支持 Blender 3.6+ 版本
- 需要在 Blender addon 进程中执行，通过 socket 与 MCP server 通信

## Goals / Non-Goals

**Goals:**

- 用 9 个工具（8 核心 + 1 可选）覆盖 99.9% 的 Blender 功能
- 统一的 CRUD 接口，通过 `DataType` 参数化
- 支持操作符上下文覆盖，解决 `bpy.ops` 的上下文依赖问题
- 提供 LLM 必需的元信息（操作反馈、历史、统计）
- 保持与现有安全层的兼容性

**Non-Goals:**

- 不实现 Modal 交互操作（需要持续用户输入）
- 不实现消息订阅/回调注册（需要持久化回调函数）
- 不实现 GPU 直接绘制（需要 draw 循环）
- 不在本变更中实现 batch 批量操作优化
- 不修改现有的传输层和协议

## Decisions

### 1. 工具分层架构

**决策**：采用三层架构：数据层（CRUD）、操作层（execute）、信息层（query）

**理由**：
- 与 Blender API 结构对齐（bpy.data / bpy.ops / bpy.context）
- 清晰的职责划分，易于理解和扩展
- 每层可独立演进

**备选方案**：
- 单一通用工具：过于复杂，参数爆炸
- 按领域分组（modeling/animation/...）：仍然会产生大量工具

### 2. DataType 枚举设计

**决策**：使用字符串枚举，包含真实数据块类型和伪类型（context/preferences）

**理由**：
- 字符串易于序列化和 AI 理解
- 伪类型统一了上下文访问方式
- 可扩展，新增类型无需修改接口

**备选方案**：
- 使用 Blender 内部类型名：不够直观（如 `ID`、`bpy_struct`）
- 分离 context 为独立工具：增加工具数量，违背压缩原则

### 3. Handler Registry 模式

**决策**：每个 DataType 对应一个 Handler 类，通过装饰器注册到 Registry

```python
@HandlerRegistry.register
class ObjectHandler(BaseHandler):
    data_type = DataType.OBJECT
    def create(self, name, params): ...
    def read(self, name, path): ...
```

**理由**：
- 清晰的扩展点，新增类型只需添加 Handler
- 每个 Handler 独立测试
- 避免巨大的 switch-case

**备选方案**：
- 函数字典：缺乏结构，难以共享逻辑
- 反射自动发现：过于隐式，调试困难

### 4. 上下文覆盖实现

**决策**：`operator.execute` 接受 `context` 参数，内部使用 `bpy.context.temp_override()`

**理由**：
- Blender 3.2+ 官方推荐方式
- 线程安全，不影响其他操作
- 覆盖范围可控

**备选方案**：
- 修改全局 context：不安全，可能影响其他操作
- 预设上下文模板：不够灵活

### 5. 图像数据返回

**决策**：`data.read` 支持 `params.format: "base64"` 返回图像数据

**理由**：
- LLM 需要视觉反馈
- base64 可直接嵌入 JSON 响应
- 可选分辨率缩放减少传输量

**备选方案**：
- 返回文件路径：需要额外的文件传输机制
- 单独的 image.capture 工具：增加工具数量

### 6. script.execute 安全策略

**决策**：默认禁用，通过配置显式启用，集成现有安全层

**理由**：
- 危险功能需要明确的用户意图
- 复用现有的 allowlist/audit 机制
- 不引入额外的沙箱复杂度（依赖用户环境隔离）

**备选方案**：
- Python 沙箱：实现复杂，容易绕过
- 完全不提供：无法覆盖边缘情况

## Risks / Trade-offs

- **[参数复杂度]** 统一接口导致参数结构复杂（如嵌套属性路径）
  → 提供清晰的文档和示例，Handler 内部做参数验证

- **[上下文覆盖失败]** 某些操作可能需要特定的 area/space 类型
  → 在 headful 模式下测试覆盖范围，文档记录已知限制

- **[性能开销]** Handler 查找和参数解析增加延迟
  → 可接受，单次调用开销 < 1ms，网络延迟是主要瓶颈

- **[Breaking Change]** 现有 `scene.read`/`scene.write` 调用方需要迁移
  → 提供迁移文档，可考虑兼容层（后续决定）

- **[script.execute 滥用]** 用户可能绕过安全限制
  → 明确警告，audit 日志记录所有执行的代码

