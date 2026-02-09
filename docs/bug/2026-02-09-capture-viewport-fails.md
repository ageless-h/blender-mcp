# Bug: blender_capture_viewport Always Fails

**Date**: 2026-02-09  
**Severity**: Medium  
**Tool**: `blender_capture_viewport`

---

## Summary

`blender_capture_viewport` fails with `operation_failed` regardless of parameters.

## Reproduction

```
blender_capture_viewport(shading="SOLID", format="PNG")    → operation_failed
blender_capture_viewport(shading="WIREFRAME", format="JPEG") → operation_failed
blender_capture_viewport(camera_view=true)                 → operation_failed
```

## Suspected Cause

In `handlers/info/query.py:320-383`:

1. `bpy.context.screen` may be `None` in headless/MCP context
2. `bpy.ops.screen.screenshot` requires valid GUI window
3. Context override may fail without active 3D viewport

## Code Location

```python
# Line 330 - may fail if no screen
for area in bpy.context.screen.areas:

# Line 350 - requires GUI context
bpy.ops.screen.screenshot(filepath=tmp_path)
```

## Fix Recommendations

1. Check if `bpy.context.screen` exists before accessing
2. Use `bpy.ops.render.opengl()` as fallback
3. Add proper error message when no viewport available
