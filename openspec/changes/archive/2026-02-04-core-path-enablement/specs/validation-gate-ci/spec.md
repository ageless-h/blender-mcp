## ADDED Requirements

### Requirement: Integration tests align with test plan
Integration tests SHALL align with the documented test plan scenarios.

#### Scenario: Scenario coverage review
- **WHEN** integration tests are reviewed
- **THEN** each documented scenario has a corresponding test or placeholder

### Requirement: Minimal CI workflow exists
The project SHALL provide a minimal CI workflow covering lint, unit tests, and an integration placeholder.

#### Scenario: CI execution
- **WHEN** CI runs on a pull request
- **THEN** lint, unit tests, and integration placeholder steps execute
