# Capability Catalog

## Purpose
TBD.

## Requirements

### Requirement: Canonical capability catalog
The system SHALL define a canonical capability catalog that groups Blender features into stable capability names.

#### Scenario: Capability discovery
- **WHEN** an agent queries available capabilities
- **THEN** the system returns the canonical catalog with names and descriptions

### Requirement: Capability metadata includes version constraints
Each capability SHALL include metadata describing version constraints and known limitations.

#### Scenario: Version constrained capability
- **WHEN** a capability is unsupported on a target Blender version
- **THEN** it is marked unavailable with reason metadata

### Requirement: Capability-to-permission mapping
The catalog SHALL map each capability to required permission scopes.

#### Scenario: Permission lookup
- **WHEN** a capability is requested
- **THEN** the system resolves required permissions from the catalog before execution
