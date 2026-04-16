# Changelog

All notable changes to Blender MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- batch_execute for bulk operations
- MCP Resources for asset directory exposure
- MCP Progress for long-running operations feedback
- WebSocket transport layer
- PolyHaven integration (HDRI/textures)
- Sketchfab integration (model import)
- Statusbar auto-refresh via `bpy.app.timers` for real-time log updates

---

## [1.3.0] - 2026-04-16

### Security
- **JSON stream processing fix**: Socket server now properly buffers and parses complete JSON messages, preventing partial message attacks.
- **Request size limit**: Added 10MB max request size to prevent memory exhaustion attacks.
- **Thread-safe timer registration**: Added `_timer_lock` to prevent race conditions in timer registration.
- **Lightweight schema validation**: Added `_validate_schema()` method for basic request structure checking.
- **Rate limiter defaults**: Added `default_limit=120` req/min and `cleanup_expired()` method for memory management.
- **Input constraints**: Added `maxLength` for filepath (4096) and code (65536) parameters.
- **Audit log rotation**: Logs rotate at 10MB with max 5 backup files.

### Fixed
- **destructiveHint annotations**: Corrected 6 tools that were incorrectly marked as non-destructive.
- **Tool annotation accuracy**: All 26 tools now have correct readOnlyHint/destructiveHint/idempotentHint.

### Testing
- **Coverage improvement**: 77% coverage (up from 73%), exceeding 75% target.
- **Boundary tests**: 24 new tests for edge cases (unicode, empty values, long messages).
- **Concurrency tests**: 6 new tests for thread safety under high contention.
- **Version compatibility tests**: 19 new tests for version parsing and capability availability.
- **Total tests**: 464 (up from 329).

### CI/CD
- **Coverage job**: New coverage job with 75% fail-under threshold.
- **Blender integration matrix**: Tests run on Blender 4.2/4.5/5.0.
- **PyPI publish workflow**: Automated publishing on release, TestPyPI support for pre-release testing.
- **Auto-version tagging**: Automatic git tag creation when version changes.

### Documentation
- **Support matrix**: Updated to include Blender 5.1, expanded platform support (linux/macos/windows).

---

## [1.2.0] - 2026-04-14

### Added
- **Dynamic timeout per capability**: Replace fixed 120s timeout with tiered system — Fast (10s) for all `get_*` queries, Standard (60s) for `edit_*`/`create_*`/`modify_*`/`manage_*`, Slow (300s) for `execute_operator`/`execute_script`/`import_export`.
- **Global statusbar indicator**: MCP status (running/offline + request count + error count) displayed in Blender's bottom status bar across all editors, not just 3D viewport.
- **Popup panel (Ctrl+Shift+M)**: Floating dialog with full server controls and scrollable activity log, accessible from any editor via hotkey or clicking the statusbar indicator.
- **Activity log with UIList**: Thread-safe `OperationLog` tracking up to 200 entries with capability name, duration, success/fail status, and response preview. Filterable, clearable.
- **Multi-connection support**: Persistent client sessions — `socket_server` handles multiple sequential requests per connection and tracks active clients.
- **Dynamic node type discovery**: Runtime `_discover_node_types()` scans `bpy.types` for Node subclasses, falling back to static English name mapping. New `node_types` include option on `blender_get_scene`.
- **i18n support**: Addon UI follows Blender's language setting (Chinese/English). Uses `_t()` helper with `translate=False` to prevent unwanted auto-translation of modifier key labels.
- **Customizable hotkey**: Panel popup hotkey configurable in addon preferences (Edit > Preferences > Add-ons > Blender MCP > Hotkey Settings).

### Changed
- **UI relocated from N-panel to global**: Removed `VIEW3D_PT_blender_mcp` sidebar panel. MCP is now editor-agnostic — statusbar + popup panel.
- **Test coverage**: 329 tests (up from 312).

### Fixed
- **UI panel stats key bug**: `stats['error']` → `stats['errors']` KeyError that silently killed remaining panel draw.
- **Write-in-draw error**: Log collection population moved from `draw()` to `invoke()` to avoid "Writing to ID classes in this context" error.
- **EnumProperty registration**: Fixed 2-tuple items (missing description field) causing registration failure.

---

## [1.1.0] - 2026-04-12

### Added
- **Undo support**: All MCP write operations now push to Blender's undo stack via `bpy.ops.ed.undo_push()`. Ctrl+Z in Blender correctly reverses MCP operations.
- **Localized node name fallback**: 140+ English display-name → bl_idname mapping so `edit_nodes` works in non-English Blender environments (Chinese, Japanese, etc.). LLMs can use names like `"Principled BSDF"`, `"Material Output"`, `"Group Input"` regardless of Blender's UI language.
- **Error message propagation**: Addon error details (e.g. `operation_failed`, `addon_exception`) are now exposed in MCP tool responses for easier debugging.
- **Advanced test suite**: 10 test scenarios with ≥10 steps each covering PBR materials, modifier stacks, armature rigging, animation, geometry nodes, physics, UV/multi-material, render pipeline, collection management, and complex shaders.

### Fixed
- **RGBA socket assignment**: `set_value` on RGBA/color sockets now uses `tuple(value)` instead of list assignment, fixing `bpy_prop` type errors in Blender 5.1.
- **GeoNodes I/O initialization**: New geometry nodes modifiers auto-create `NodeGroupInput`/`NodeGroupOutput` with proper `interface.new_socket()` calls.
- **Duplicate except block**: Removed duplicate `except` clause in `base.py` that caused `IndentationError`.
- **Compositor safe access**: Added `scene.use_nodes = True` auto-enable with safe `bpy.context` fallback for timer-dispatched handlers.
- **VSE null checks**: Added null checks and detailed error logging for VSE strip creation failures.
- **Timer context guards**: All `bpy.context` accesses in timer-dispatched handlers now use `try/except` fallbacks to prevent crashes in Blender 5.1's timer dispatch.

### Changed
- **Test coverage**: 312 tests (up from 255), including 18 node editor tests with localization fallback coverage.
- **Development status**: Updated from Beta to Production/Stable in `pyproject.toml`.

### Known Limitations
- **VSE strip creation** fails in Blender 5.1 timer context (API limitation, not a bug).
- **Compositor node editing** fails in Blender 5.1 timer context (API limitation, not a bug).
- **Object reference pointers** (e.g. `GeometryNodeObjectInfo.object`) cannot be set via MCP `set_property` — requires `execute_script`.
- **Multi-material slot assignment** always replaces slot 0 — creating multiple slots requires `execute_script`.

---

## [1.0.0] - 2026-02-09

### Changed
- Version bump to 1.0.0 - first stable release
- Published to PyPI as `ageless-blender-mcp`

---

## [0.1.0] - 2026-02-08

### Added
- **Four-layer tool architecture** with 26 specialized tools:
  - **Perception Layer** (11 tools): Deep Blender state querying
  - **Declarative Write Layer** (3 tools): Node/animation/VSE editing
  - **Imperative Write Layer** (9 tools): Object/material/modifier operations
  - **Fallback Layer** (3 tools): Operator/script/import-export
- Complete test coverage: 255 tests across 4 test files
- Error code system: 15 error codes across 5 categories
- Response schema validation with helper functions
- Full type annotations for public APIs
- Comprehensive documentation:
  - Tool capability catalog (`docs/capabilities/catalog.md`)
  - Layer-specific documentation (perception/declarative/imperative)
  - Architecture docs (core-lifecycle, transport, protocol-transport, plugin-boundary)
  - Testing guides (integration-test-plan, ci-matrix)
  - Migration guide from old 8-tool architecture
  - 15+ client-specific integration guides

### Fixed
- **P0 Critical Bugs**:
  - `data-create-mesh-geometry-failure`: Fixed vertex/edge/face count 0 when creating mesh primitives
  - `data-create-curve-splines-lost`: Fixed spline data loss when creating curves
  - `data-create-text-unsupported`: Implemented complete text object creation
  - `data-create-metaball-unsupported`: Added metaball support with elements creation
  - `data-create-grease-pencil-unsupported`: Implemented grease pencil object creation
- **P1 Parameter Conversion Layer**:
  - Fixed `include` parameter not working in `blender_get_object_data`
  - Fixed `filter` parameter incomplete implementation in `blender_get_objects`
  - Fixed `include` parameter not working in `blender_get_scene`
  - Fixed `depth` parameter for recursive collections in `blender_get_collections`
  - Fixed `include` and `bone_filter` in `blender_get_armature_data`
  - Fixed parameter passing in `blender_capture_viewport`
  - Fixed parameter mapping in `blender_create_object`, `blender_modify_object`, `blender_manage_material`

### Changed
- Removed payload wrapper layer - all parameters now exposed directly in inputSchema
- Updated all tools to use `blender_` prefix for multi-server compatibility
- Tool names now follow MCP specification (underscores instead of hyphens)
- Response format now includes structured segmentation for scene queries

### Improved
- Handler implementations now support granular `include` options (12 types for objects)
- Collection reading supports recursive depth control
- Armature reading supports bone filtering with glob patterns
- Material PBR parameter extraction for create/edit operations

### Breaking Changes
- Old tool names (`data_create`, `data_read`, etc.) are now mapped but deprecated
- Legacy compatibility maintained through automatic mapping layer

---

## Legend

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Improved**: Non-breaking improvements

[Unreleased]: https://github.com/ageless-h/blender-mcp/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/ageless-h/blender-mcp/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ageless-h/blender-mcp/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ageless-h/blender-mcp/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/ageless-h/blender-mcp/releases/tag/v0.1.0
