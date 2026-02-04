## Why

能力集在扩展中缺少统一的测试与示例交付底线，导致回归风险高、CI 无法证明“能力执行路径”稳定。需要把“每新增能力必须带示例与集成测试、并纳入 CI 覆盖”提升为明确的规范与门禁，以保证能力迭代可持续。

## What Changes

- 规定能力交付的测试与示例底线：每新增能力或能力扩展必须同时提供
  - 1 个可运行示例（example）
  - 1 个覆盖该能力关键路径的集成测试（integration test）
- 明确测试基线：测试框架约定、基线用例、假实现（mocks/fakes）的边界与复用方式
- 扩展 CI 覆盖能力执行路径：CI 不仅运行 lint/unit，还应执行与测试计划对齐的能力路径集成用例
- 分阶段策略：本提案优先落地交付/验收与 CI 门禁两条主线，其他测试线（示例强化、解析与错误码契约测试、能力目录引用）作为后续阶段补齐以减少冲突

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `integration-tests-and-examples`: 补齐“每新增能力必须带 1 个示例 + 1 个集成测试”的验收规范，并定义测试框架/基线用例/mocks 约束
- `validation-gate-ci`: 将 CI 从“integration placeholder”升级为覆盖能力执行路径的门禁，并要求与测试计划/场景对齐

## Impact

- 代码与目录结构
  - `tests/`: 需要按能力/场景建立可扩展的集成测试基线，并引入可复用的 mocks/fakes
  - `examples/`: 示例需要与能力验收规范对齐（可发现、可运行、可验证）
- CI
  - `.github/workflows/ci.yml`: 增强门禁步骤，覆盖能力执行路径的集成用例执行与结果呈现
- 后续阶段（本提案的延伸）
  - `runnable-examples`: 强化“示例可运行与可验证”的规范
  - `jsonrpc-parse-errors`: 增补解析与错误码的契约测试/回归基线
  - `capability-catalog`: 仅增加一处对 `integration-tests-and-examples` 规范的引用以避免重复
