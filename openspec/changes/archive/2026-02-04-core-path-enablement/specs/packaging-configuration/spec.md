## ADDED Requirements

### Requirement: Packaging uses PEP 621 metadata
The project SHALL define packaging metadata in `pyproject.toml` using PEP 621 fields.

#### Scenario: Metadata review
- **WHEN** packaging metadata is reviewed
- **THEN** name, version, dependencies, and scripts are defined under `[project]`

### Requirement: Package discovery is limited to src
The build system SHALL discover packages only under `src/`.

#### Scenario: Build package discovery
- **WHEN** the build backend resolves packages
- **THEN** it only includes modules from `src/`

### Requirement: Installable package provides stable import path
The installed package SHALL provide a stable import path `blender_mcp`.

#### Scenario: Runtime import
- **WHEN** a user imports the package
- **THEN** `import blender_mcp` succeeds after installation
