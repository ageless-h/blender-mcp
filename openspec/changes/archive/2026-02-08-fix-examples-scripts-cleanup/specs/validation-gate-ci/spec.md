## MODIFIED Requirements

### Requirement: Minimal CI workflow exists
The project SHALL provide a minimal CI workflow covering lint, unit tests, and scenario-based integration tests. Compatibility validation SHALL be handled by a single matrix-based job; there SHALL NOT be duplicate jobs performing the same validation.

#### Scenario: CI execution
- **WHEN** CI runs on a pull request
- **THEN** lint, unit tests, and integration test steps execute

#### Scenario: No duplicate compatibility jobs
- **WHEN** the CI workflow is reviewed
- **THEN** exactly one job handles Blender version compatibility checks (the matrix-based `blender-compat` job)
