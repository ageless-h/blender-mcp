## ADDED Requirements

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
