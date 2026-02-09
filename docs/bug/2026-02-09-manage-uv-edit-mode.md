# Bug: blender_manage_uv Edit Mode Operations Fail

**Date**: 2026-02-09  
**Severity**: Medium  
**Tool**: `blender_manage_uv`

---

## Summary

`blender_manage_uv` partially works. Operations requiring Edit Mode fail, others succeed.

## Test Results

| Action | Status | Requires Edit Mode |
|--------|--------|-------------------|
| `add_uv_map` | ✅ Success | No |
| `smart_project` | ❌ operation_failed | Yes |

## Root Cause

UV unwrap operations (`smart_project`, `unwrap`, etc.) require:
1. Object must be in Edit Mode
2. Mesh elements must be selected
3. Proper context override

## Fix Recommendations

Wrap edit-mode operations with mode switching:
```python
original_mode = obj.mode
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
# ... do UV operation ...
bpy.ops.object.mode_set(mode=original_mode)
```
