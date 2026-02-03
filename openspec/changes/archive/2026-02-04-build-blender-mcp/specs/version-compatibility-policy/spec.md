## ADDED Requirements

### Requirement: LTS and latest support policy
The project SHALL maintain an explicit support matrix that includes Blender LTS releases and the latest stable release.

#### Scenario: Support matrix published
- **WHEN** a release is prepared
- **THEN** the support matrix is updated to include LTS and latest versions

### Requirement: Compatibility checks per supported version
The system SHALL run compatibility checks for each supported Blender version before release.

#### Scenario: Compatibility failure
- **WHEN** a supported version fails compatibility checks
- **THEN** the release is blocked until resolved or the support matrix is updated

### Requirement: Deprecation and rollback policy
The project SHALL define a deprecation and rollback policy for dropping version support.

#### Scenario: Dropping a non-LTS version
- **WHEN** a non-LTS version is removed from support
- **THEN** the change is documented with migration guidance and timelines
