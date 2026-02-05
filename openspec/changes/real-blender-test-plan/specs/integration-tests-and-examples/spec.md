# Integration Tests and Examples (Delta)

## Purpose

扩展现有集成测试规范，增加针对真实 Blender 的测试场景要求。

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Integration tests use a stable harness and defined fakes boundary

The project SHALL provide a stable integration test harness for constructing an MCP server bundle and SHALL define where mocks/fakes are permitted to isolate external dependencies. Additionally, the project SHALL provide a real Blender harness for end-to-end testing that communicates with actual Blender processes.

#### Scenario: Integration tests are implemented consistently

- **WHEN** a contributor adds a new integration scenario
- **THEN** the test uses the shared harness to construct the server and uses project-approved mocks/fakes only at defined boundaries

#### Scenario: Real Blender tests use BlenderProcessHarness

- **WHEN** a contributor adds a real Blender integration test
- **THEN** the test SHALL use `BlenderProcessHarness` to manage the Blender process lifecycle

