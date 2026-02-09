# Bug: Server Crash & Operator Instability (Threading Violation)

**Date:** 2026-02-09
**Component:** `socket_server.py`
**Status:** **FIXED**

## Description
The Blender MCP server spawns a new `threading.Thread` for each client request and calls the internal `execute_capability` function directly on this background thread.
Blender's Python API (`bpy`) is **not thread-safe**. Accessing `bpy.data` or `bpy.ops` from outside the main thread results in:
1.  **Process Crashes**: Random Segfaults/Access Violations when requests overlap.
2.  **Operator Failures**: Tools like `create_object` (primitives), `manage_physics`, `import_export`, and `manage_uv` fail sporadically with `operation_failed` or `context` errors because Blender cannot correctly deduce the context (Active Object, Mode) from a background thread.

## Root Cause
Architecture violation: `socket_server.py` does not dispatch requests to the Blender Main Thread (e.g. via `bpy.app.timers`).

## Current Impact
- **High Concurrency**: Immediate Crash.
- **Sequential Execution**: No Crash, but Operator-based tools (`create_object`, `import_export`) are unreliable (approx 50% failure rate).
- **Data Access**: Read-only tools (`get_objects`, `get_scene`) are generally stable but technically unsafe.

## Fix Applied
Implemented `queue.Queue` + `bpy.app.timers` loop in `socket_server.py`:
- Background threads (`_handle_client`) put requests into `_dispatch_queue` via `_dispatch_to_main_thread()` and block until done.
- `_main_thread_poll()` timer callback drains the queue on Blender's main thread, executing `execute_capability()` safely.
- Timer is registered on server start (`_ensure_timer_registered`) and unregistered on stop (`_unregister_timer`).
