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

[Unreleased]: https://github.com/ageless-h/blender-mcp/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/ageless-h/blender-mcp/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ageless-h/blender-mcp/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/ageless-h/blender-mcp/releases/tag/v0.1.0
