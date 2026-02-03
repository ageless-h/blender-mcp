## ADDED Requirements

### Requirement: Core package naming is stable
The core service package SHALL use a stable, lowercase package name aligned with the repository name.

#### Scenario: Import path consistency
- **WHEN** new modules are added
- **THEN** import paths remain under a single package root

### Requirement: Module layering is enforced
Core modules SHALL be grouped by responsibility (core, transport, adapters, security, catalog, versioning, validation).

#### Scenario: New capability module
- **WHEN** a new capability module is introduced
- **THEN** it is placed under the appropriate responsibility group
