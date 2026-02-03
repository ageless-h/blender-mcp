## ADDED Requirements

### Requirement: Integration example is runnable
The project SHALL provide a runnable integration example that exercises the stdio transport path.

#### Scenario: Example execution
- **WHEN** the integration example is run
- **THEN** it completes with a successful exit status

### Requirement: Minimal CI structure is defined
The project SHALL define a minimal CI workflow with lint, unit tests, and an integration placeholder.

#### Scenario: CI execution
- **WHEN** CI runs on a pull request
- **THEN** lint, unit, and integration placeholder steps execute
