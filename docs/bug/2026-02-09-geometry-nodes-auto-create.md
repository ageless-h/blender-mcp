# Bug: Geometry Nodes Tree Auto-Creation Missing

**Date**: 2026-02-09  
**Severity**: High  
**Tool**: `blender_edit_nodes` (GEOMETRY context)

---

## Summary

Cannot edit geometry nodes on a new modifier because auto-creation of node_group is not implemented.

## Reproduction

```python
# 1. Create object with NODES modifier
blender_create_object(name="Test")
blender_manage_modifier(action="add", object_name="Test", modifier_type="NODES", modifier_name="GN")

# 2. Try to edit nodes - FAILS
blender_edit_nodes(tree_type="GEOMETRY", context="MODIFIER", target="Test/GN", operations=[...])
→ Error: not_found
```

## Root Cause

In `handlers/nodes/reader.py:88-96`:
```python
if mod and mod.type == "NODES" and mod.node_group:  # ← node_group is None!
    return mod.node_group
return None  # ← Always returns None for new modifiers
```

In `handlers/nodes/editor.py:32-48`:
- Auto-creates SHADER node trees ✅
- Auto-creates COMPOSITOR node trees ✅
- Does NOT auto-create GEOMETRY node trees ❌

## Fix

Add to `editor.py` after line 42:

```python
if tree_type == "GEOMETRY" and context == "MODIFIER" and target and "/" in target:
    obj_name, mod_name = target.split("/", 1)
    obj = bpy.data.objects.get(obj_name)
    if obj:
        mod = obj.modifiers.get(mod_name)
        if mod and mod.type == "NODES" and not mod.node_group:
            # Create new geometry node group
            node_group = bpy.data.node_groups.new(mod_name, "GeometryNodeTree")
            # Add Group Input/Output nodes
            node_group.nodes.new("NodeGroupInput")
            node_group.nodes.new("NodeGroupOutput")
            mod.node_group = node_group
            node_tree = node_group
```
