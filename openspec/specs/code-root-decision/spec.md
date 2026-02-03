# Code Root Decision

## Purpose
TBD.

## Requirements

### Requirement: Single code root is enforced
The project SHALL use a single authoritative code root and reject dual root layouts.

#### Scenario: Layout selection
- **WHEN** the code root is selected
- **THEN** only one layout is supported and documented

### Requirement: src layout is authoritative
The project SHALL treat `src/blender_mcp/` as the authoritative code root.

#### Scenario: Import resolution
- **WHEN** code is imported after installation
- **THEN** imports resolve from `src/blender_mcp/` without ambiguity

### Requirement: Migration path is documented
The project SHALL document how existing root-level code is migrated to `src/`.

#### Scenario: Migration guidance
- **WHEN** a contributor migrates modules
- **THEN** they can follow a documented path without changing runtime behavior
