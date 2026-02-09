# Bug: blender_get_collections Default Root Name Wrong

**Date**: 2026-02-09  
**Severity**: Low  
**Tool**: `blender_get_collections`

---

## Summary

`blender_get_collections` fails with `not_found` when called without parameters because the default root collection name is incorrect.

## Reproduction

```
# Fails - uses default "Scene Collection"
blender_get_collections()
→ Error: not_found

# Works - specify actual collection name
blender_get_collections(root="Collection")
→ Returns collection data successfully
```

## Root Cause

In `base.py:121-125`:
```python
if capability == "blender.get_collections":
    ...
    return data_read({..., "name": payload.get("root", "Scene Collection")}, ...)
```

The default value `"Scene Collection"` is wrong. Blender's default collection is named `"Collection"`.

## Fix

Change line 125 in `base.py`:
```diff
- return data_read({..., "name": payload.get("root", "Scene Collection")}, ...)
+ return data_read({..., "name": payload.get("root", "Collection")}, ...)
```

Or better: use `bpy.context.scene.collection.name` as the default.
