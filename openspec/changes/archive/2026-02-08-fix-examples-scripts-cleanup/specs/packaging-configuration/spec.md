## ADDED Requirements

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
