# Render Still

## Purpose
TBD.

## Requirements

### Requirement: `render-still` capability is defined in the catalog
The system SHALL define a capability entry for still render execution with canonical metadata.

#### Scenario: Capability metadata
- **WHEN** a contributor inspects the capability catalog
- **THEN** it contains an entry with:
  - **name**: `render.still`
  - **description**: identifies still render execution
  - **scopes**: includes `render:execute`
  - **min_version**: `3.6`
  - **max_version**: omitted or null

### Requirement: `render.still` requests require the declared scope
The system SHALL reject `render.still` requests that do not provide the required scope.

#### Scenario: Missing `render:execute` scope
- **WHEN** an agent invokes `render.still` without the `render:execute` scope
- **THEN** the request is rejected with an authorization error
