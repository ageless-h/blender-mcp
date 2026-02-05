# Integration Tests and Examples

## Purpose

提供集成测试和示例，演示安全、正确的能力使用，并支持在真实 Blender 安装上进行端到端测试。

## Requirements

### Requirement: Scenario-based integration tests
The project SHALL define scenario-based integration tests covering critical agent workflows.

#### Scenario: Critical workflow coverage
- **WHEN** integration tests are run
- **THEN** each critical workflow has at least one passing scenario

### Requirement: Cross-version test execution
Integration tests SHALL execute across all supported Blender versions.

#### Scenario: Multi-version test run
- **WHEN** tests are executed in CI
- **THEN** results are reported per supported Blender version

### Requirement: Example workflows provided
The project SHALL provide example workflows demonstrating safe, correct capability usage.

#### Scenario: Example discovery
- **WHEN** a developer explores the repository
- **THEN** example workflows are documented and runnable

### Requirement: Capability changes include an example and an integration test
The project SHALL require that each new capability, and each capability change that adds new behavior, includes at least one runnable example and at least one scenario-based integration test covering the capability execution path.

#### Scenario: New capability submission includes artifacts
- **WHEN** a contributor introduces a new capability or extends an existing capability
- **THEN** the change includes:
  - a runnable example under `examples/` demonstrating correct usage
  - an integration test under `tests/integration/` that exercises the capability through the server request handling path

### Requirement: Integration tests use a stable harness and defined fakes boundary
The project SHALL provide a stable integration test harness for constructing an MCP server bundle and SHALL define where mocks/fakes are permitted to isolate external dependencies. Additionally, the project SHALL provide a real Blender harness for end-to-end testing that communicates with actual Blender processes.

#### Scenario: Integration tests are implemented consistently
- **WHEN** a contributor adds a new integration scenario
- **THEN** the test uses the shared harness to construct the server and uses project-approved mocks/fakes only at defined boundaries

#### Scenario: Real Blender tests use BlenderProcessHarness
- **WHEN** a contributor adds a real Blender integration test
- **THEN** the test SHALL use `BlenderProcessHarness` to manage the Blender process lifecycle

### Requirement: Real Blender integration test suite

The project SHALL provide integration tests that execute against real Blender installations, not just mocks.

#### Scenario: Real Blender test discovery
- **WHEN** a developer runs `pytest tests/integration/real_blender/`
- **THEN** tests SHALL execute against configured Blender executables

#### Scenario: Skip when no Blender configured
- **WHEN** no Blender paths are configured
- **THEN** real Blender tests SHALL be skipped with informative message

### Requirement: Multi-version test execution

The project SHALL support running tests against multiple Blender versions in sequence.

#### Scenario: Parametrized version testing
- **WHEN** multiple Blender versions are configured
- **THEN** each test SHALL run against each configured version

#### Scenario: Version-specific test results
- **WHEN** multi-version tests complete
- **THEN** results SHALL be reported separately per Blender version

### Requirement: Compatibility results export

The project SHALL export real Blender test results to the compatibility results file.

#### Scenario: Update compatibility-results.json
- **WHEN** `scripts/run_real_blender_tests.py` completes
- **THEN** results SHALL be written to `docs/versioning/compatibility-results.json`

#### Scenario: Results include version and status
- **WHEN** results are exported
- **THEN** each entry SHALL include `version`, `status`, `timestamp`, and `test_count`
