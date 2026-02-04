## Why

目前仓库已有 capability catalog / minimum capability set 等规范骨架，但内容仍偏抽象（TBD）且实现侧缺少一组可验证、最小闭环的能力定义（scene/object/render）。这导致 capabilities 的发现、权限(scopes)映射、以及 Blender 版本约束(version constraints)在文档与实现之间难以一致地演进与测试。

## What Changes

- 定义 5–10 个最小、稳定命名的能力（覆盖 `scene` / `object` / `render` 方向），作为 MVP 的 canonical capability set。
- 为每个能力明确：
  - 需要的 permission scopes（用于 capability-to-permission mapping）。
  - Blender 版本约束与已知限制（用于 capability metadata / availability 标注）。
- 对齐能力目录(capability catalog)的文档与实现：
  - 文档侧提供清晰的 capability 条目（名称、描述、scopes、version constraints）。
  - 实现侧提供同源/一致的数据结构，并在示例启动路径中注册最小能力集，保证可发现与可测试。

## Capabilities

### New Capabilities
- `scene-read`: 读取场景级信息（如场景元数据、帧范围、单位、基础设置）并以结构化结果返回。
- `object-read`: 读取对象及其基础属性（名称、类型、变换、可见性、集合归属等）。
- `object-transform-write`: 写入对象变换（location/rotation/scale）等最小编辑能力。
- `object-selection-write`: 变更对象选择/激活状态，用于驱动后续操作的最小交互能力。
- `render-settings-read`: 读取渲染相关设置（引擎、分辨率、采样等）用于规划/解释渲染行为。
- `render-still`: 执行单帧渲染并返回产物引用/路径（或可配置为返回 bytes/metadata）。
- `render-animation`: 执行动画/帧范围渲染并返回产物引用/路径与进度/结果摘要。

### Modified Capabilities
<!-- None. Existing specs remain the source of requirements; this change fills in the minimal catalog content and aligns implementation without changing spec-level requirements. -->

## Impact

- OpenSpec 文档：新增上述能力各自的 `specs/<capability>/spec.md`，并补齐 capability catalog 中的最小条目集与示例说明（不改变既有 requirement 语义）。
- 代码实现：在 capability catalog 的实现侧增加与文档对齐的数据结构（name/description/scopes/version constraints/availability reason），并在 stdio 示例启动时注册最小能力集。
- 测试/示例：需要能通过一个最小用例验证 capability discovery 返回的 catalog 与实现一致，且能对版本不满足的能力正确标注不可用原因。
