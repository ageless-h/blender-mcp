# Tool Migration Guide: scene.* → Unified Tools

This guide helps migrate from the legacy `scene.read`/`scene.write` capabilities to the new unified tool architecture.

## Overview

The legacy capabilities (`scene.read`, `scene.write`) are **deprecated** and will be removed in a future version. The new unified tool architecture provides:

- **8 core tools** that cover 99.9% of Blender functionality
- **Parameterized data access** via `type` parameter instead of separate capabilities per data type
- **Universal operator execution** instead of per-operator capabilities
- **Comprehensive info queries** for LLM feedback

## Migration Table

| Legacy Capability | New Tool | Example |
|-------------------|----------|---------|
| `scene.read` | `data.read` with `type="context"` | See below |
| `scene.write` (create object) | `data.create` with `type="object"` | See below |
| N/A | `operator.execute` | Execute any bpy.ops.* |
| N/A | `info.query` | Get reports, stats, viewport capture |

## Detailed Migration Examples

### Reading Scene State

**Before (legacy):**
```json
{
  "capability": "scene.read",
  "payload": {}
}
```

**After (new):**
```json
{
  "capability": "data.read",
  "payload": {
    "type": "context"
  }
}
```

The response now includes more information:
- `mode`: Current editing mode
- `active_object`: Active object name
- `selected_objects`: List of selected object names
- `scene`: Current scene name
- `view_layer`: Current view layer
- `workspace`: Current workspace

### Creating Objects

**Before (legacy):**
```json
{
  "capability": "scene.write",
  "payload": {
    "name": "MyCube",
    "cleanup": false
  }
}
```

**After (new):**
```json
{
  "capability": "data.create",
  "payload": {
    "type": "object",
    "name": "MyCube",
    "params": {
      "object_type": "MESH",
      "location": [0, 0, 0]
    }
  }
}
```

### Reading Object Properties

**New (no legacy equivalent):**
```json
{
  "capability": "data.read",
  "payload": {
    "type": "object",
    "name": "Cube",
    "path": "location"
  }
}
```

### Writing Object Properties

**New (no legacy equivalent):**
```json
{
  "capability": "data.write",
  "payload": {
    "type": "object",
    "name": "Cube",
    "properties": {
      "location": [1, 2, 3],
      "scale": [2, 2, 2]
    }
  }
}
```

### Executing Operators

**New (no legacy equivalent):**
```json
{
  "capability": "operator.execute",
  "payload": {
    "operator": "mesh.primitive_cube_add",
    "params": {
      "size": 2.0,
      "location": [0, 0, 0]
    }
  }
}
```

With context override:
```json
{
  "capability": "operator.execute",
  "payload": {
    "operator": "mesh.subdivide",
    "params": {"number_cuts": 2},
    "context": {
      "mode": "EDIT",
      "active_object": "Cube"
    }
  }
}
```

### Querying Information

**New (no legacy equivalent):**
```json
{
  "capability": "info.query",
  "payload": {
    "type": "scene_stats"
  }
}
```

Available query types:
- `reports`: Recent operation reports
- `last_op`: Last operation details
- `undo_history`: Undo stack
- `scene_stats`: Scene statistics (vertex count, etc.)
- `selection`: Current selection state
- `mode`: Current editing mode
- `viewport_capture`: Capture viewport as base64

## New Tool Reference

### data.create
Create new Blender data blocks.
```json
{"capability": "data.create", "payload": {"type": "<DataType>", "name": "<name>", "params": {...}}}
```

### data.read
Read properties from data blocks.
```json
{"capability": "data.read", "payload": {"type": "<DataType>", "name": "<name>", "path": "<optional.path>"}}
```

### data.write
Write properties to data blocks.
```json
{"capability": "data.write", "payload": {"type": "<DataType>", "name": "<name>", "properties": {...}}}
```

### data.delete
Delete data blocks.
```json
{"capability": "data.delete", "payload": {"type": "<DataType>", "name": "<name>"}}
```

### data.list
List all data blocks of a type.
```json
{"capability": "data.list", "payload": {"type": "<DataType>", "filter": {...}}}
```

### data.link
Link/unlink data blocks.
```json
{"capability": "data.link", "payload": {"source": {"type": "...", "name": "..."}, "target": {"type": "...", "name": "..."}, "unlink": false}}
```

### operator.execute
Execute any Blender operator.
```json
{"capability": "operator.execute", "payload": {"operator": "<category>.<name>", "params": {...}, "context": {...}}}
```

### info.query
Query Blender state and metadata.
```json
{"capability": "info.query", "payload": {"type": "<query_type>", "params": {...}}}
```

## Supported DataTypes

Core: `object`, `mesh`, `curve`, `surface`, `metaball`, `armature`, `lattice`

Appearance: `material`, `texture`, `image`, `world`, `linestyle`

Light/Camera: `camera`, `light`, `probe`

Nodes: `node_tree`

Organization: `collection`, `scene`, `workspace`

Animation: `action`, `grease_pencil`

Special: `context` (pseudo-type), `preferences` (pseudo-type)

Attached: `modifier`, `constraint` (require `params.object`)

## Deprecation Timeline

- **Current**: Legacy capabilities work but emit deprecation warnings
- **Next Major**: Legacy capabilities removed

We recommend migrating to the new unified tools as soon as possible.
