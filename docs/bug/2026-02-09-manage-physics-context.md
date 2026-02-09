# Bug: blender_manage_physics Context Override Issue

**Date**: 2026-02-09  
**Severity**: Medium  
**Tool**: `blender_manage_physics`

---

## Summary

`blender_manage_physics` fails with `operation_failed` for all physics types due to missing context override.

## Reproduction

```
blender_manage_physics(action="add", object_name="Cube", physics_type="RIGID_BODY")
→ operation_failed

blender_manage_physics(action="add", object_name="TestCube", physics_type="CLOTH")
→ operation_failed
```

## Root Cause

In `handlers/physics/handler.py:43-45`:

```python
# This alone is not sufficient for bpy.ops
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
```

The `bpy.ops` calls (lines 71-88) require proper context override:

```python
bpy.ops.rigidbody.object_add()      # Line 71 - needs Rigid Body World
bpy.ops.object.modifier_add()        # Lines 73-77 - needs context override
```

## Fix Recommendations

1. Use `bpy.context.temp_override()` for all operator calls
2. For RIGID_BODY, ensure scene has a Rigid Body World first
3. Add proper exception handling with meaningful messages

Example fix:
```python
with bpy.context.temp_override(active_object=obj, object=obj, selected_objects=[obj]):
    bpy.ops.object.modifier_add(type="CLOTH")
```
