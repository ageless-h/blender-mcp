## Context

- 当前实现中能力元数据主要由 `blender_mcp.catalog.catalog.CapabilityMeta` 表达（`name/description/scopes/min_version/max_version`），并通过 `CapabilityCatalog.register()` 注册。
- 示例启动 `examples/stdio_loop.py` 会创建 `CapabilityCatalog` 并注册 `minimal_capability_set()`，但 `MCPServer` 本身目前不持有 catalog，也未通过 transport 暴露“能力发现 / 列举”能力。
- 权限校验路径已经存在：`MCPServer.handle_request()` 基于 `PermissionPolicy.capability_scopes` 判断是否满足 required scopes；allowlist 与 rate limit 亦基于 capability name 工作。
- 现状的 `minimal_capability_set()` 仅包含 2 条能力（`scene.read`, `scene.write`），且版本约束字段尚未被使用。

## Goals / Non-Goals

**Goals:**

- 定义 5–10 个最小能力，覆盖 `scene` / `object` / `render`，并为每个能力提供：
  - `scopes`（用于权限映射与授权校验）
  - `min_version` / `max_version`（用于版本可用性判定与原因说明）
- 在实现侧建立“单一事实来源”：
  - `minimal_capability_set()` 作为 MVP 的 canonical set（可被示例启动、测试与未来 server discovery 复用）。
- 能力目录与实现对齐：
  - 文档（capability catalog + 每个 capability spec）与代码中的条目字段一致。
  - 对能力命名与 scopes/版本约束的格式做出明确决策，避免 drift。

**Non-Goals:**

- 不在本变更中实现真实的 Blender 业务操作（如实际渲染、对象变换执行等）。
- 不引入复杂的权限模型（如条件权限、分层继承、动态 scope 计算）。
- 不在本变更中引入新的外部依赖（版本解析优先使用 stdlib 方案）。

## Decisions

1. **能力命名（Capability Name）**

   - 代码侧继续沿用现有点分命名（例如 `scene.read`、`scene.write`），以避免对现有示例与测试产生不必要破坏。
   - OpenSpec 中新增 capability 的 spec 文件目录名使用 kebab-case（例如 `scene-read/ spec.md`），但 spec 内容中明确声明运行时 capability name 为点分命名（例如 `scene.read`）。
   - 目的：兼容 OpenSpec 的文件组织习惯，同时保持运行时标识符稳定。

2. **Scopes 命名与映射**

   - scopes 采用现有冒号分隔风格（例如 `scene:write`、`object:write`、`render:execute`）。
   - `PermissionPolicy.capability_scopes` 继续作为“capability -> required scopes”映射的权威位置；能力目录中的 `CapabilityMeta.scopes` 与之保持一致，避免出现两套规则。

3. **版本约束（Version Constraints）表达与判定**

   - 复用 `CapabilityMeta.min_version` / `max_version` 字段：
     - `min_version`: 语义为“包含式下界”（>=）。
     - `max_version`: 语义为“排他式上界”（<），用于表达已知不兼容的未来版本区间。
   - 实现侧提供一个轻量版本比较函数（以 `major.minor.patch` 数字元组比较为主），不引入外部依赖。
   - 当目标 Blender 版本不满足约束时，catalog 可生成 `available: false` 与 `reason`（例如 `version_out_of_range`）。

4. **能力发现（Discovery）与返回结构**

   - 将能力发现作为一个标准能力（例如 `capabilities.list`）纳入最小集（或作为 catalog 专属能力），使其同样受 allowlist/permissions/rate limit 管控。
   - `capabilities.list` 的返回结构为能力条目数组，每项包含：
     - `name`, `description`, `scopes`, `min_version`, `max_version`
     - `available`（可选，基于目标 Blender 版本计算）
     - `unavailable_reason`（可选）
   - 为实现该能力，`MCPServer` 需要注入并持有 `CapabilityCatalog`（新增字段），并在 `handle_request()` 中对 `capabilities.list` 做特殊处理（直接返回 catalog 序列化结果）。

5. **最小能力集合内容（初版）**

   - 最小集沿 proposal 的意图扩展到 5–10 条，运行时命名采用点分：
     - `scene.read`
     - `object.read`
     - `object.transform.write`
     - `object.selection.write`
     - `render.settings.read`
     - `render.still`
     - `render.animation`
   - 每条能力在 `minimal_capability_set()` 中写明 `scopes` 与（如适用）`min_version/max_version`。

## Risks / Trade-offs

- **[命名风格不一致（proposal kebab-case vs runtime dot-case）]** → 通过在 specs 中显式声明“spec 文件名/目录”与“runtime capability name”的映射来缓解，并在后续 specs 工件中统一表述。
- **[版本比较实现过于简化]** → 限定支持 `x.y` 或 `x.y.z` 数字版本；遇到非数字后缀时以保守策略处理，并在文档中约束版本字符串格式。
- **[catalog 与 PermissionPolicy 双源漂移]** → 规定 `CapabilityMeta.scopes` 作为来源并自动/显式生成 `PermissionPolicy.capability_scopes` 的初始化（或在测试中断言两者一致）。
- **[引入 server 持有 catalog 的结构变更]** → 通过依赖注入（构建时传入）而非全局单例，保证测试可控且影响面可追踪。
