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

[Unreleased]: https://github.com/ageless-h/blender-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ageless-h/blender-mcp/releases/tag/v0.1.0
