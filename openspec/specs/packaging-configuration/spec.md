# Packaging Configuration

## Purpose
TBD.

## Requirements

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

### Requirement: Non-installed execution uses shared path fix
Directories that contain runnable scripts (examples/, scripts/) SHALL each provide a _pathfix.py module that adds src/ to sys.path, following the same pattern as tests/_pathfix.py.

#### Scenario: Script runs without installation
- **WHEN** a developer runs a script from examples/ or scripts/ without installing the package
- **THEN** the script successfully imports blender_mcp via its local _pathfix.py module

### Requirement: No dead entry points in repository root
The repository root SHALL NOT contain dead or placeholder entry point files. If a root-level main.py exists, it SHALL delegate to a functional entry point.

#### Scenario: Root main.py absence
- **WHEN** the repository root is inspected
- **THEN** no non-functional main.py exists
