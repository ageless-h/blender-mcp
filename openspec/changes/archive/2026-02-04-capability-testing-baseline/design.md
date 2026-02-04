## Context

- 当前已有的规范与实现基础
  - `openspec/specs/integration-tests-and-examples/spec.md` 已定义“关键工作流场景集成测试”和“示例工作流可发现/可运行”，但缺少“能力新增必须带示例+集成测试”的可执行验收口径，以及测试基线/假实现约定。
  - `openspec/specs/validation-gate-ci/spec.md` 已要求 CI 覆盖 lint、单测、integration placeholder，并要求存在可运行的 stdio 路径示例，但尚未把“能力执行路径覆盖”变为门禁。
- 代码仓内现状
  - CI：`.github/workflows/ci.yml` 的 `integration` job 目前运行 `python -m unittest tests.integration.test_workflows`（placeholder）以及 `python -m examples.stdio_loop`。
  - 集成测试：`tests/integration/test_workflows.py` 已覆盖 allowlist/permissions/rate-limit 等“能力执行路径”的核心分支，是后续扩展的良好起点。

约束：
- 维持当前项目基线（`unittest` + 现有目录结构），避免引入新的外部依赖与大规模重构。
- CI 运行在 `ubuntu-latest`，应避免引入需要真实 Blender 的重型端到端路径（除非后续阶段另行设计）。

## Goals / Non-Goals

**Goals:**
- 将“每新增能力必须带 1 个示例 + 1 个集成测试”落实为可执行的交付/验收规范（权威位置：`integration-tests-and-examples`）。
- 建立可复用的测试基线与假实现约定：
  - 统一集成测试的场景组织方式
  - 统一 server/harness 构建、mocks/fakes 的边界
- 将 CI 从“integration placeholder”提升为覆盖能力执行路径的门禁（权威位置：`validation-gate-ci`），并与测试计划/场景对齐。

**Non-Goals:**
- 不引入新的运行时 capability（本提案属于质量门禁/交付规范）。
- 不在本阶段要求 CI 运行真实 Blender 或做完整 E2E（可作为后续扩展）。
- 不将所有已有能力一次性补齐到完全覆盖（采用“增量约束”：新能力/新增需求必须满足）。

## Decisions

1) 权威规则落点与去重策略
- 权威规则落在 `integration-tests-and-examples`：定义能力交付必须包含“示例 + 集成测试”的验收条款，以及最低基线。
- `capability-catalog`（后续阶段）仅增加一句“引用 `integration-tests-and-examples` 的交付规范”，避免重复与冲突。

2) 集成测试基线组织方式（在不引入新框架的前提下）
- 继续使用 `unittest`。
- 在 `tests/integration/` 内引入“场景分组”的惯例（具体目录/命名由后续 specs 明确）：
  - 保留并扩展 `test_workflows.py` 作为“关键工作流场景”基线
  - 新增能力时：新增一个与能力/场景对应的 `test_*.py`，并复用统一的 harness 构建方法
- 将 server/harness 的构建逻辑从单个测试文件中抽出为共享构件（例如一个 `tests/integration/_harness.py` 形式的模块），以减少重复并规范 mocks/fakes 使用边界。

3) “每新增能力必须带示例 + 集成测试”的可验证机制
- 先采用“规范约束 + CI 执行覆盖”的组合：
  - 规范层面：明确新增能力必须提交示例与集成测试的验收条款
  - CI 层面：integration job 运行集成测试套件 + 运行示例
- 后续可选增强（不在本阶段强制落地）：新增一个轻量的校验脚本/测试，用于检查“变更引入的新 capability/新增 spec”是否同时包含示例与集成测试入口（避免只靠人工 review）。

4) CI 门禁扩展策略（覆盖能力执行路径）
- 将 `.github/workflows/ci.yml` 的 integration job 从固定测试模块（placeholder）调整为运行集成测试集合（例如按目录 discover 或显式列表），确保新增能力对应的集成测试会被执行。
- 继续保留并扩展 `python -m examples.stdio_loop` 等示例执行；后续按能力增量增加示例执行清单（避免一次性把所有示例都跑导致 CI 时间爆炸）。

5) 分阶段落地（降低冲突）
- 阶段 1（本变更主线）：
  - 改 `integration-tests-and-examples`
  - 改 `validation-gate-ci`
- 阶段 2（后续阶段）：
  - `runnable-examples`：补齐“示例可运行/可验证”细则与与能力绑定方式
  - `jsonrpc-parse-errors`：补齐解析与错误码的契约测试基线
  - `capability-catalog`：仅加对阶段 1 规范的引用

## Risks / Trade-offs

- [CI 时间增加] → 通过分层执行与清单化示例运行（只跑关键/新增能力的示例）控制时长。
- [规则难以自动强制] → 先以规范+CI 覆盖为门槛，后续再引入轻量校验脚本/测试，避免一开始引入高耦合机制。
- [集成测试易变得脆弱/难维护] → 通过统一 harness、明确 mocks/fakes 边界、以“场景”而非内部实现细节编写断言来降低脆弱性。
