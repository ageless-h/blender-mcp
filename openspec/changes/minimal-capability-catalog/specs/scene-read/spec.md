## ADDED Requirements

### Requirement: `scene-read` capability is defined in the catalog
The system SHALL define a capability entry for scene read access with canonical metadata.

#### Scenario: Capability metadata
- **WHEN** a contributor inspects the capability catalog
- **THEN** it contains an entry with:
  - **name**: `scene.read`
  - **description**: identifies scene-level read access
  - **scopes**: includes `scene:read`
  - **min_version**: `3.6`
  - **max_version**: omitted or null

### Requirement: `scene.read` requests require the declared scope
The system SHALL reject `scene.read` requests that do not provide the required scope.

#### Scenario: Missing `scene:read` scope
- **WHEN** an agent invokes `scene.read` without the `scene:read` scope
- **THEN** the request is rejected with an authorization error
