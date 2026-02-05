# Operator Execution

## Purpose
TBD.

## Requirements

### Requirement: operator.execute tool
The system SHALL provide an `operator.execute` tool that executes any Blender operator (bpy.ops.*).

#### Scenario: Execute simple operator
- **WHEN** `operator.execute` is called with `operator="mesh.primitive_cube_add"`, `params={"size": 2.0}`
- **THEN** system executes the operator and adds a cube to the scene
- **AND** returns `{"success": true, "operator": "mesh.primitive_cube_add", "result": "FINISHED"}`

#### Scenario: Execute operator with context override
- **WHEN** `operator.execute` is called with `operator="mesh.subdivide"`, `params={"number_cuts": 2}`, `context={"mode": "EDIT", "active_object": "Cube"}`
- **THEN** system switches to edit mode for Cube, executes subdivide, and returns success

#### Scenario: Execute import operator
- **WHEN** `operator.execute` is called with `operator="import_scene.fbx"`, `params={"filepath": "/path/to/model.fbx"}`
- **THEN** system imports the FBX file and returns success with import details

#### Scenario: Execute export operator
- **WHEN** `operator.execute` is called with `operator="export_scene.gltf"`, `params={"filepath": "/path/to/output.glb", "export_format": "GLB"}`
- **THEN** system exports the scene to GLTF format

#### Scenario: Execute render operator
- **WHEN** `operator.execute` is called with `operator="render.render"`, `params={"write_still": true}`
- **THEN** system renders the current frame and saves to output path

#### Scenario: Operator execution failure
- **WHEN** `operator.execute` is called with an invalid context or parameters
- **THEN** system returns `{"success": false, "result": "CANCELLED", "reports": [...]}`
- **AND** reports array contains error messages

### Requirement: Context override support
The system SHALL support context override parameter to set execution environment before running operators.

#### Scenario: Override active object
- **WHEN** `context={"active_object": "Sphere"}` is provided
- **THEN** system sets Sphere as active object before executing the operator

#### Scenario: Override mode
- **WHEN** `context={"mode": "SCULPT"}` is provided
- **THEN** system switches to sculpt mode before executing the operator

#### Scenario: Override selection
- **WHEN** `context={"selected_objects": ["Cube", "Sphere"]}` is provided
- **THEN** system selects specified objects before executing the operator

#### Scenario: Override area type
- **WHEN** `context={"area_type": "NODE_EDITOR"}` is provided
- **THEN** system uses node editor context for the operator execution

### Requirement: Operator result reporting
The system SHALL return detailed execution results including success status, operator result, and any reports.

#### Scenario: Successful execution with info report
- **WHEN** operator executes successfully with informational output
- **THEN** response includes `reports` array with `{"type": "INFO", "message": "..."}`

#### Scenario: Execution with warnings
- **WHEN** operator executes with warnings
- **THEN** response includes `reports` array with `{"type": "WARNING", "message": "..."}`

#### Scenario: Execution timing
- **WHEN** any operator is executed
- **THEN** response includes `duration_ms` field with execution time in milliseconds
