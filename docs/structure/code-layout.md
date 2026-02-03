# Code Layout Conventions

## Package Root
- Core service code lives under `src/blender_mcp/`.
- The package name MUST remain stable and lowercase.

## Module Grouping
Core modules are grouped by responsibility:
- `core/`
- `transport/`
- `adapters/`
- `security/`
- `catalog/`
- `versioning/`
- `validation/`

## Migration Note
Existing modules outside `src/` should be migrated incrementally, with a compatibility note in release notes.
