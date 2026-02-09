# Bug: blender_import_export Fails to Export

**Date:** 2026-02-09
**Tool:** `blender_import_export` (Action: `export`)
**Status:** **FIXED** (root cause was threading violation)

## Description
The `blender_import_export` tool fails to export existing objects (e.g., OBJ/GLTF). It returns `Error: operation_failed`.

## Steps to Reproduce
1. Create a mesh object (e.g., `ObjExpTest`).
2. Select it.
3. Call `blender_import_export(action="export", format="OBJ", filepath="test.obj")`.
4. Result: **FAIL** (`operation_failed`).

## Analysis
- **Context Dependency**: Most exporter operators (like `bpy.ops.wm.obj_export`) require a valid 3D View context and selection state.
- **Threading Issue**: This tool is severely impacted by `server-threading-crash`. Executing IO operators from a background thread is known to be unstable in Blender.

## Fix Applied
Fixed by resolving root cause in `socket_server.py` — all requests now dispatch to Blender's main thread via `queue.Queue` + `bpy.app.timers`. See `2026-02-09-server-threading-crash.md`.
