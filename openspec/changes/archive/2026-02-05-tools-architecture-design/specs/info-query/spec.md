## ADDED Requirements

### Requirement: info.query tool
The system SHALL provide an `info.query` tool that retrieves status, history, and metadata information from Blender.

#### Scenario: Query operation reports
- **WHEN** `info.query` is called with `type="reports"`
- **THEN** system returns recent operation reports including info, warnings, and errors

#### Scenario: Query with limit parameter
- **WHEN** `info.query` is called with `type="reports"`, `params={"limit": 10}`
- **THEN** system returns at most 10 most recent reports

### Requirement: Last operation query
The system SHALL support querying the last executed operation and its result.

#### Scenario: Query last operation
- **WHEN** `info.query` is called with `type="last_op"`
- **THEN** system returns `{"operator": "...", "success": true/false, "result": "...", "reports": [...], "duration_ms": ...}`

#### Scenario: Query last operation parameters
- **WHEN** `info.query` is called with `type="last_op"` after an operation
- **THEN** response includes `params` field with the parameters used

### Requirement: Undo history query
The system SHALL support querying the undo history.

#### Scenario: Query undo history
- **WHEN** `info.query` is called with `type="undo_history"`
- **THEN** system returns list of undo steps with index, name, and current marker

#### Scenario: Query undo availability
- **WHEN** `info.query` is called with `type="undo_history"`
- **THEN** response includes `can_undo` and `can_redo` boolean fields

### Requirement: Scene statistics query
The system SHALL support querying scene statistics.

#### Scenario: Query scene stats
- **WHEN** `info.query` is called with `type="scene_stats"`
- **THEN** system returns object count, vertex count, edge count, face count, and memory usage

#### Scenario: Query render settings
- **WHEN** `info.query` is called with `type="scene_stats"`
- **THEN** response includes render engine, current frame, frame range

### Requirement: Selection state query
The system SHALL support querying current selection state.

#### Scenario: Query selection in object mode
- **WHEN** `info.query` is called with `type="selection"` in object mode
- **THEN** system returns active_object, selected_objects list, and selected_count

#### Scenario: Query selection in edit mode
- **WHEN** `info.query` is called with `type="selection"` in edit mode
- **THEN** system returns edit_mesh statistics including selected verts, edges, and faces

### Requirement: Mode query
The system SHALL support querying current editing mode.

#### Scenario: Query current mode
- **WHEN** `info.query` is called with `type="mode"`
- **THEN** system returns mode, mode_string, active_object, object_type, tool, and workspace

### Requirement: Change tracking query
The system SHALL support querying changes since last query.

#### Scenario: Query changes
- **WHEN** `info.query` is called with `type="changes"`
- **THEN** system returns modified_objects, added_objects, deleted_objects lists

#### Scenario: Query geometry updates
- **WHEN** `info.query` is called with `type="changes"`
- **THEN** response includes geometry_updates and transform_updates lists

### Requirement: Viewport capture
The system SHALL support capturing viewport images.

#### Scenario: Capture current viewport
- **WHEN** `info.query` is called with `type="viewport_capture"`, `params={"format": "base64"}`
- **THEN** system returns base64 encoded image of current viewport

#### Scenario: Capture with resolution
- **WHEN** `info.query` is called with `type="viewport_capture"`, `params={"resolution": [1920, 1080]}`
- **THEN** system returns image at specified resolution

#### Scenario: Capture with shading mode
- **WHEN** `info.query` is called with `type="viewport_capture"`, `params={"shading": "RENDERED"}`
- **THEN** system captures viewport with rendered shading mode

#### Scenario: Capture to filepath
- **WHEN** `info.query` is called with `type="viewport_capture"`, `params={"format": "filepath"}`
- **THEN** system saves image to file and returns the path

### Requirement: Version information query
The system SHALL support querying Blender version information.

#### Scenario: Query version
- **WHEN** `info.query` is called with `type="version"`
- **THEN** system returns blender_version, blender_version_string, api_version, and python_version

### Requirement: Memory usage query
The system SHALL support querying memory usage.

#### Scenario: Query memory
- **WHEN** `info.query` is called with `type="memory"`
- **THEN** system returns total_mb, used_mb, peak_mb, and per-category memory breakdown

