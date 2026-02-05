# Object Transform Write

## Purpose
TBD.

## Requirements

### Requirement: `object-transform-write` capability is defined in the catalog
The system SHALL define a capability entry for object transform write access with canonical metadata.

#### Scenario: Capability metadata
- **WHEN** a contributor inspects the capability catalog
- **THEN** it contains an entry with:
  - **name**: `object.transform.write`
  - **description**: identifies object transform write access
  - **scopes**: includes `object:write`
  - **min_version**: `3.6`
  - **max_version**: omitted or null

### Requirement: `object.transform.write` requests require the declared scope
The system SHALL reject `object.transform.write` requests that do not provide the required scope.

#### Scenario: Missing `object:write` scope
- **WHEN** an agent invokes `object.transform.write` without the `object:write` scope
- **THEN** the request is rejected with an authorization error
