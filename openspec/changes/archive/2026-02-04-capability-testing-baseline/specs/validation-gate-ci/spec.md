## MODIFIED Requirements

### Requirement: Minimal CI workflow exists
The project SHALL provide a minimal CI workflow covering lint, unit tests, and scenario-based integration tests.

#### Scenario: CI execution
- **WHEN** CI runs on a pull request
- **THEN** lint, unit tests, and integration test steps execute

## ADDED Requirements

### Requirement: Integration CI gates capability execution paths
CI SHALL execute the integration test suite that covers critical capability execution paths and SHALL fail the workflow if any scenario fails.

#### Scenario: Failing integration scenario blocks merge
- **WHEN** an integration scenario fails in CI
- **THEN** the CI workflow fails and reports the failing scenario
