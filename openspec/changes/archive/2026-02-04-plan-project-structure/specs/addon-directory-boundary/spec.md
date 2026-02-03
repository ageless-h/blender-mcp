## ADDED Requirements

### Requirement: Addon code is isolated in its own directory
Blender addon code SHALL live in a dedicated top-level directory separate from core service code.

#### Scenario: Addon isolation review
- **WHEN** the addon is updated
- **THEN** changes are limited to the addon directory and its documented interfaces

### Requirement: Addon boundary is documented
The addon directory SHALL define a contract surface that documents entrypoints and supported API versions.

#### Scenario: Contract verification
- **WHEN** the core service integrates with the addon
- **THEN** it validates the addon contract version and entrypoints
