# Bug: blender_manage_uv Fails

**Date:** 2026-02-09
**Tool:** `blender_manage_uv`
**Status:** **FIXED** (root cause was threading violation)

## Description
The `blender_manage_uv` tool fails to perform UV unwrap operations (e.g., `smart_project`).

## Steps to Reproduce
1. Create a mesh object.
2. Call `blender_manage_uv(action="smart_project", object_name="...")`.
3. Result: **FAIL** (`operation_failed`).

## Analysis
UV operators like `uv.smart_project` strictly require the object to be in **EDIT MODE** and the context to be correct (Active Object).
**Update (2026-02-09):** This failure is highly correlated with the **Threading Violation** bug (`server-threading-crash`). Because the operator runs on a background thread, `bpy.ops.object.mode_set(mode='EDIT')` successfully changes the mode *internally*, but the subsequent UV operator may not see the correct Context/Window/Area because those are bound to the Main Thread.

## Fix Applied
Fixed by resolving root cause in `socket_server.py` — all requests now dispatch to Blender's main thread via `queue.Queue` + `bpy.app.timers`. See `2026-02-09-server-threading-crash.md`.
