## ADDED Requirements

### Requirement: Addon package location
The Blender addon SHALL be packaged at `src/blender_mcp_addon/` as a proper Python package installable via Blender's addon preferences.

#### Scenario: Package is importable
- **WHEN** the addon directory is installed to Blender's addons folder
- **THEN** Blender can import the package and read bl_info

### Requirement: bl_info metadata dictionary
The addon SHALL define a `bl_info` dictionary in `__init__.py` with required Blender addon metadata.

#### Scenario: bl_info contains required fields
- **WHEN** Blender loads the addon
- **THEN** bl_info provides: name, author, version, blender (min version), category, description

#### Scenario: Blender version compatibility
- **WHEN** bl_info specifies blender minimum version
- **THEN** it supports Blender 3.6 LTS and 4.x series

### Requirement: register() and unregister() functions
The addon SHALL implement `register()` and `unregister()` functions as Blender entrypoints.

#### Scenario: Addon registration
- **WHEN** user enables the addon in Blender preferences
- **THEN** register() is called and all addon components are activated

#### Scenario: Addon unregistration
- **WHEN** user disables the addon in Blender preferences
- **THEN** unregister() is called and all addon components are cleanly removed

#### Scenario: Socket server lifecycle tied to registration
- **WHEN** addon is registered
- **THEN** socket server can be started via operator or auto-start preference

### Requirement: Package internal structure
The addon package SHALL organize code into logical modules for maintainability.

#### Scenario: Module organization
- **WHEN** the addon package is structured
- **THEN** it separates: operators, preferences, capabilities, and socket server code

#### Scenario: Capability handlers isolated
- **WHEN** execute_capability receives a request
- **THEN** capability handlers are in dedicated modules (e.g., capabilities/scene.py)

### Requirement: Backward compatibility with existing entrypoints
The addon SHALL maintain compatibility with the existing `execute_capability()` contract.

#### Scenario: execute_capability contract preserved
- **WHEN** socket server receives a capability request
- **THEN** the response format matches the existing contract (ok, result, error, timing_ms)
