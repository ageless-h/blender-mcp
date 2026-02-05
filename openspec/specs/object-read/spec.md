# Object Read

## Purpose
TBD.

## Requirements

### Requirement: `object-read` capability is defined in the catalog
The system SHALL define a capability entry for object read access with canonical metadata.

#### Scenario: Capability metadata
- **WHEN** a contributor inspects the capability catalog
- **THEN** it contains an entry with:
  - **name**: `object.read`
  - **description**: identifies object-level read access
  - **scopes**: includes `object:read`
  - **min_version**: `3.6`
  - **max_version**: omitted or null

### Requirement: `object.read` requests require the declared scope
The system SHALL reject `object.read` requests that do not provide the required scope.

#### Scenario: Missing `object:read` scope
- **WHEN** an agent invokes `object.read` without the `object:read` scope
- **THEN** the request is rejected with an authorization error
