# Minimum Capability Set

## Purpose
TBD.

## Requirements

### Requirement: Minimum capability set is defined
The project SHALL define a minimal capability set using the new unified tool architecture, replacing the previous fine-grained capability naming.

#### Scenario: Capability review
- **WHEN** a contributor inspects the catalog
- **THEN** the minimal set includes the 8 core tools: data.create, data.read, data.write, data.delete, data.list, data.link, operator.execute, info.query

#### Scenario: Tool registration
- **WHEN** the MCP server initializes
- **THEN** all 8 core tools are registered with their metadata (name, description, scopes, version constraints)

#### Scenario: Optional tool availability
- **WHEN** script.execute is enabled in configuration
- **THEN** it is included in the capability set with appropriate security warnings

### Requirement: Scope mapping for unified tools
The system SHALL define scope mappings for the new unified tools that integrate with the existing permission system.

#### Scenario: Data tool scopes
- **WHEN** data.* tools are registered
- **THEN** scopes are mapped based on type parameter (e.g., object:read, object:write, material:read)

#### Scenario: Operator tool scopes
- **WHEN** operator.execute is called
- **THEN** required scopes are derived from operator category (e.g., render:execute, import:execute)

#### Scenario: Info tool scopes
- **WHEN** info.query is called
- **THEN** required scope is info:read

#### Scenario: Script tool scopes
- **WHEN** script.execute is called
- **THEN** required scope is script:execute (highest privilege level)

### Requirement: Capability catalog update
The system SHALL update the CapabilityCatalog to reflect the new tool architecture.

#### Scenario: Catalog registration
- **WHEN** minimal_capability_set() is called
- **THEN** returns CapabilityMeta entries for all 8 core tools

#### Scenario: Version constraints
- **WHEN** capability metadata is generated
- **THEN** each tool includes min_version="3.6" constraint
