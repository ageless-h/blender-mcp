# Validation Gate CI

## Purpose
TBD.

## Requirements

### Requirement: Integration tests align with test plan
Integration tests SHALL align with the documented test plan scenarios.

#### Scenario: Scenario coverage review
- **WHEN** integration tests are reviewed
- **THEN** each documented scenario has a corresponding test or placeholder

### Requirement: Minimal CI workflow exists
The project SHALL provide a minimal CI workflow covering lint, unit tests, and scenario-based integration tests. Compatibility validation SHALL be handled by a single matrix-based job; there SHALL NOT be duplicate jobs performing the same validation.

#### Scenario: CI execution
- **WHEN** CI runs on a pull request
- **THEN** lint, unit tests, and integration test steps execute

#### Scenario: No duplicate compatibility jobs
- **WHEN** the CI workflow is reviewed
- **THEN** exactly one job handles Blender version compatibility checks (the matrix-based `blender-compat` job)

### Requirement: Integration CI gates capability execution paths
CI SHALL execute the integration test suite that covers critical capability execution paths and SHALL fail the workflow if any scenario fails.

#### Scenario: Failing integration scenario blocks merge
- **WHEN** an integration scenario fails in CI
- **THEN** the CI workflow fails and reports the failing scenario

### Requirement: Integration example is runnable
The project SHALL provide a runnable integration example that exercises the stdio transport path.

#### Scenario: Example execution
- **WHEN** the integration example is run
- **THEN** it completes with a successful exit status
