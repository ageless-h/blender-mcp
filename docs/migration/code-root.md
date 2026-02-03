# Code Root Migration

## Summary
The authoritative code root is now `src/blender_mcp/`. The root-level `blender_mcp/` directory is deprecated and will be removed after migration.

## Migration Steps
1. Move modules from `blender_mcp/` to `src/blender_mcp/`.
2. Update any import paths that referenced the root-level package.
3. Verify tests and packaging after the move.

## Notes
Avoid introducing new code under the root-level package.
