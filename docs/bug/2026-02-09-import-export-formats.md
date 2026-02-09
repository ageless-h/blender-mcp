# Bug: blender_import_export Only FBX Works

**Date**: 2026-02-09  
**Severity**: Medium  
**Tool**: `blender_import_export`

---

## Summary

Only FBX format works. GLB, OBJ, STL, GLTF all fail.

## Test Results

| Format | Operator | Result |
|--------|----------|--------|
| FBX | `export_scene.fbx` | ✅ Success |
| GLB | `export_scene.gltf` | ❌ operation_failed |
| OBJ | `wm.obj_export` | ❌ operation_failed |
| STL | `wm.stl_export` | ❌ operation_failed |
| GLTF | `export_scene.gltf` | ❌ operation_failed |

## Suspected Cause

1. `wm.*` operators may have different parameter requirements
2. GLTF exporter needs `export_format` parameter correctly set
3. Blender version differences in operator IDs

## Location

`handlers/importexport/handler.py:26-40` (operator mapping)
