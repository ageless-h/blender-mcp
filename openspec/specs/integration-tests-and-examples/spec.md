# Integration Tests and Examples

## Purpose
TBD.

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
The project SHALL provide a stable integration test harness for constructing an MCP server bundle and SHALL define where mocks/fakes are permitted to isolate external dependencies.

#### Scenario: Integration tests are implemented consistently
- **WHEN** a contributor adds a new integration scenario
- **THEN** the test uses the shared harness to construct the server and uses project-approved mocks/fakes only at defined boundaries
