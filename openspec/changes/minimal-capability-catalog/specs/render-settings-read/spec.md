## ADDED Requirements

### Requirement: `render-settings-read` capability is defined in the catalog
The system SHALL define a capability entry for render settings read access with canonical metadata.

#### Scenario: Capability metadata
- **WHEN** a contributor inspects the capability catalog
- **THEN** it contains an entry with:
  - **name**: `render.settings.read`
  - **description**: identifies render settings read access
  - **scopes**: includes `render:read`
  - **min_version**: `3.6`
  - **max_version**: omitted or null

### Requirement: `render.settings.read` requests require the declared scope
The system SHALL reject `render.settings.read` requests that do not provide the required scope.

#### Scenario: Missing `render:read` scope
- **WHEN** an agent invokes `render.settings.read` without the `render:read` scope
- **THEN** the request is rejected with an authorization error
