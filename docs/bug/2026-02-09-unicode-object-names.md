# Bug: Unicode Object Names Cause Failures

**Date**: 2026-02-09  
**Severity**: Medium  
**Affected Tools**: `blender_get_object_data`, `blender_get_animation_data`

---

## Summary

Multiple MCP tools fail when querying objects with Chinese/Unicode names.

## Affected Tools

| Tool | Error Type |
|------|------------|
| `blender_get_object_data` | `operation_failed` |
| `blender_get_animation_data` | `addon_exception` |

## Reproduction

```
# blender_get_object_data - Fails
blender_get_object_data(name="苏珊娜", include=["summary"])
→ Error: operation_failed

# blender_get_object_data - Works  
blender_get_object_data(name="TestCube", include=["summary"])
→ Success

# blender_get_animation_data - Fails
blender_get_animation_data(target="苏珊娜", include=["keyframes"])
→ Error: addon_exception

# blender_get_animation_data - Works
blender_get_animation_data(target="TestCube", include=["keyframes"])
→ Success
```

## Test Results

| Object Name | get_object_data | get_animation_data |
|-------------|-----------------|-------------------|
| `TestCube` | ✅ | ✅ |
| `Camera` | ✅ | ✅ |
| `Light` | ✅ | ✅ |
| `苏珊娜` | ❌ | ❌ |

## Suspected Cause

Shared data handler layer has UTF-8 encoding bug in object lookup.

## Fix Recommendations

Add explicit Unicode normalization in data handlers.
