# Tool Schema Optimization — Design Document

## Architecture Overview

### Three-Layer Design

```
┌─────────────────────────────────────────────────────────────┐
│  Perception Layer (11 tools)  — LLM's "eyes"               │
│  Read Blender state deeply with controllable granularity    │
├─────────────────────────────────────────────────────────────┤
│  Declarative Write Layer (3 tools) — LLM's "creative hands"│
│  Node editor (6 contexts) + Animation + VSE Sequencer       │
├─────────────────────────────────────────────────────────────┤
│  Imperative Write Layer (9 tools) — Basic scene operations  │
│  Object/Material/Modifier/UV/Constraint/Physics/Scene       │
├─────────────────────────────────────────────────────────────┤
│  Fallback Layer (3 tools) — Escape hatches                  │
│  execute_operator + execute_script + import_export          │
└─────────────────────────────────────────────────────────────┘
```

### Schema Design Principles

1. **Flat parameters** — No `payload` wrapper; all params are top-level inputSchema properties
2. **Enum constraints** — Every categorical parameter uses `enum` to limit valid values
3. **Descriptive fields** — Every parameter has `description`, and where applicable: `default`, `minimum`, `maximum`, `minItems`, `maxItems`
4. **Tool descriptions** — Each tool description states: what it does, when to use it, and when NOT to use it (referencing the correct tool)
5. **additionalProperties: false** — Prevent LLM from inventing parameters
6. **blender_ prefix** — All tool names prefixed to avoid collision in multi-server environments

### Tool Annotations

Every tool carries MCP annotations:

| Annotation | Meaning |
|------------|---------|
| `readOnlyHint` | Does not modify Blender state |
| `destructiveHint` | Deletes data or makes irreversible changes |
| `idempotentHint` | Repeated calls produce same result |
| `openWorldHint` | Accesses external network (always false for us) |

---

## Perception Layer (11 Tools)

### 1. blender_get_objects

**Description**: List objects in the Blender scene with optional filters. Returns name, type, location, and collection for each object. Use this as the first call to understand what exists in a scene.

**Annotations**: readOnly=true, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "type_filter": {
      "type": "string",
      "enum": ["MESH", "LIGHT", "CAMERA", "CURVE", "EMPTY", "ARMATURE", "LATTICE", "FONT", "GPENCIL", "SPEAKER", "VOLUME"],
      "description": "Filter by object type."
    },
    "collection": {
      "type": "string",
      "description": "Filter by collection name. Only returns objects in this collection."
    },
    "selected_only": {
      "type": "boolean",
      "default": false,
      "description": "If true, only return currently selected objects."
    },
    "visible_only": {
      "type": "boolean",
      "default": false,
      "description": "If true, only return objects visible in viewport."
    },
    "name_pattern": {
      "type": "string",
      "description": "Glob pattern to filter by name (e.g. 'SM_*' or '*_high')."
    }
  },
  "additionalProperties": false
}
```

**Internal mapping**: ObjectHandler.list_items + filter logic

---

### 2. blender_get_object_data

**Description**: Get detailed data for a single object. Use the `include` parameter to control which data is returned, avoiding context overflow. For armature-specific data (bone hierarchy, poses), use blender_get_armature_data instead.

**Annotations**: readOnly=true, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Name of the object to inspect."
    },
    "include": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["summary", "mesh_stats", "modifiers", "materials", "constraints", "physics", "animation", "custom_properties", "vertex_groups", "shape_keys", "uv_maps", "particle_systems"]
      },
      "default": ["summary"],
      "description": "Which data sections to include. Use 'summary' for a quick overview."
    }
  },
  "required": ["name"],
  "additionalProperties": false
}
```

**Internal mapping**: ObjectHandler.read + type-specific handlers based on include

---

### 3. blender_get_node_tree

**Description**: Read the structure of any node tree in Blender — shader nodes, compositor nodes, or geometry nodes. Returns nodes (name, type, inputs, outputs, location) and links (connections between nodes). Supports all 6 node tree contexts.

**Annotations**: readOnly=true, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "tree_type": {
      "type": "string",
      "enum": ["SHADER", "COMPOSITOR", "GEOMETRY"],
      "description": "Type of node tree to read."
    },
    "context": {
      "type": "string",
      "enum": ["OBJECT", "WORLD", "LINESTYLE", "SCENE", "MODIFIER", "TOOL"],
      "description": "Context within the tree type. SHADER: OBJECT|WORLD|LINESTYLE. COMPOSITOR: SCENE. GEOMETRY: MODIFIER|TOOL."
    },
    "target": {
      "type": "string",
      "description": "Target name. For SHADER/OBJECT: material name. For SHADER/WORLD: world name (default: active world). For SHADER/LINESTYLE: linestyle name. For GEOMETRY/MODIFIER: 'ObjectName/ModifierName'. For GEOMETRY/TOOL: tool asset name."
    },
    "depth": {
      "type": "string",
      "enum": ["summary", "full"],
      "default": "summary",
      "description": "Level of detail. 'summary' returns node names and types only. 'full' returns all parameters and connections."
    }
  },
  "required": ["tree_type", "context"],
  "additionalProperties": false
}
```

**Internal mapping**: New handler — reads node_tree.nodes and node_tree.links

---

### 4. blender_get_animation_data

**Description**: Read animation data for an object or scene — keyframes, F-Curves, NLA strips, drivers, and shape keys. Use blender_edit_animation to modify this data.

**Annotations**: readOnly=true, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "target": {
      "type": "string",
      "description": "Object name, or 'scene' for scene-level animation data."
    },
    "include": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["keyframes", "fcurves", "nla", "drivers", "shape_keys"]
      },
      "default": ["keyframes"],
      "description": "Which animation data to include."
    },
    "frame_range": {
      "type": "array",
      "items": {"type": "integer"},
      "minItems": 2,
      "maxItems": 2,
      "description": "Optional [start, end] frame range to limit keyframe data."
    }
  },
  "required": ["target"],
  "additionalProperties": false
}
```

**Internal mapping**: info_query(type=animation) or new animation reader

---

### 5. blender_get_materials

**Description**: List all materials in the file with their basic properties (name, use_nodes, user count, base PBR values). For detailed node tree structure, use blender_get_node_tree with tree_type=SHADER.

**Annotations**: readOnly=true, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "filter": {
      "type": "string",
      "enum": ["all", "used_only", "unused_only"],
      "default": "all",
      "description": "Filter materials by usage status."
    },
    "name_pattern": {
      "type": "string",
      "description": "Glob pattern to filter by name (e.g. '*Metal*')."
    }
  },
  "additionalProperties": false
}
```

**Internal mapping**: MaterialHandler.list_items + filter logic

---

### 6. blender_get_scene

**Description**: Get scene-level global information — statistics, render engine config, world environment basics, timeline/FPS, Blender version, memory usage. This is the high-level project overview.

**Annotations**: readOnly=true, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "include": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["stats", "render", "world", "timeline", "version", "memory"]
      },
      "default": ["stats", "render", "timeline"],
      "description": "Which sections to include in the response."
    }
  },
  "additionalProperties": false
}
```

**Internal mapping**: info_query(type=scene_stats/version/memory) + bpy.context.scene properties

---

### 7. blender_get_collections

**Description**: Return the collection hierarchy tree. Each collection shows name, child collections, object count, viewport/render visibility, and color tag.

**Annotations**: readOnly=true, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "root": {
      "type": "string",
      "description": "Start from this collection. Default: Scene Collection (root)."
    },
    "depth": {
      "type": "integer",
      "minimum": 1,
      "default": 10,
      "description": "Maximum recursion depth for the tree."
    }
  },
  "additionalProperties": false
}
```

**Internal mapping**: CollectionHandler.read + recursive traversal

---

### 8. blender_get_armature_data

**Description**: Read armature/bone data — bone hierarchy, head/tail/roll positions, bone constraints, rest/pose transforms, bone groups, IK chains. This is separate from blender_get_object_data because armature data is complex and deeply nested.

**Annotations**: readOnly=true, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "armature_name": {
      "type": "string",
      "description": "Name of the armature object."
    },
    "include": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["hierarchy", "poses", "constraints", "bone_groups", "ik_chains"]
      },
      "default": ["hierarchy"],
      "description": "Which data sections to include."
    },
    "bone_filter": {
      "type": "string",
      "description": "Glob pattern to filter bones by name (e.g. 'Arm*' or '*_L')."
    }
  },
  "required": ["armature_name"],
  "additionalProperties": false
}
```

**Internal mapping**: ArmatureHandler.read + bone iteration + constraint reading

---

### 9. blender_get_images

**Description**: List all images/textures in the file — name, dimensions, format, file path, packed status, color space, user count. Essential for texture asset management and detecting missing files.

**Annotations**: readOnly=true, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "filter": {
      "type": "string",
      "enum": ["all", "packed", "external", "missing", "unused"],
      "default": "all",
      "description": "Filter images by status."
    },
    "name_pattern": {
      "type": "string",
      "description": "Glob pattern to filter by name."
    }
  },
  "additionalProperties": false
}
```

**Internal mapping**: New handler — iterates bpy.data.images

---

### 10. blender_capture_viewport

**Description**: Capture a screenshot of the current 3D viewport. This is the LLM's only way to "see" the visual result. Supports different shading modes and camera view.

**Annotations**: readOnly=true, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "shading": {
      "type": "string",
      "enum": ["SOLID", "MATERIAL", "RENDERED", "WIREFRAME"],
      "default": "SOLID",
      "description": "Viewport shading mode for the capture."
    },
    "camera_view": {
      "type": "boolean",
      "default": false,
      "description": "If true, capture from the active camera's perspective."
    },
    "format": {
      "type": "string",
      "enum": ["PNG", "JPEG"],
      "default": "PNG",
      "description": "Image format for the capture."
    }
  },
  "additionalProperties": false
}
```

**Internal mapping**: info_query(type=viewport_capture) with extended params

---

### 11. blender_get_selection

**Description**: Return the current selection state — selected objects, active object, current interaction mode (Object/Edit/Sculpt/Pose/...), and active tool. Use this to understand what the user is currently working on.

**Annotations**: readOnly=true, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false
}
```

**Internal mapping**: info_query(type=selection) + info_query(type=mode)

---

## Declarative Write Layer (3 Tools)

### 12. blender_edit_nodes ⭐

**Description**: Edit any node tree in Blender — add/remove nodes, connect/disconnect sockets, set node input values and properties. Supports all 6 node tree contexts: object shader, world shader, line style shader, scene compositor, geometry nodes modifier, and geometry nodes tool. Operations are executed in order within a single call, allowing complete node graph construction in one invocation. For reading node trees, use blender_get_node_tree.

**Annotations**: readOnly=false, destructive=false, idempotent=false

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "tree_type": {
      "type": "string",
      "enum": ["SHADER", "COMPOSITOR", "GEOMETRY"],
      "description": "Type of node tree to edit."
    },
    "context": {
      "type": "string",
      "enum": ["OBJECT", "WORLD", "LINESTYLE", "SCENE", "MODIFIER", "TOOL"],
      "description": "Context within the tree type. SHADER: OBJECT|WORLD|LINESTYLE. COMPOSITOR: SCENE. GEOMETRY: MODIFIER|TOOL."
    },
    "target": {
      "type": "string",
      "description": "Target name. For SHADER/OBJECT: material name. For SHADER/WORLD: world name. For SHADER/LINESTYLE: linestyle name. For GEOMETRY/MODIFIER: 'ObjectName/ModifierName'. For GEOMETRY/TOOL: tool asset name. For COMPOSITOR/SCENE: omit or scene name."
    },
    "operations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "action": {
            "type": "string",
            "enum": ["add_node", "remove_node", "connect", "disconnect", "set_value", "set_property"],
            "description": "The node operation to perform."
          },
          "type": {
            "type": "string",
            "description": "For add_node: Blender node type identifier (e.g. 'ShaderNodeBsdfPrincipled', 'CompositorNodeGlare', 'GeometryNodeDistributePointsOnFaces')."
          },
          "name": {
            "type": "string",
            "description": "Node name. For add_node: desired name for the new node. For remove_node: name of node to remove."
          },
          "location": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 2,
            "maxItems": 2,
            "description": "For add_node: [x, y] position in the node editor."
          },
          "node": {
            "type": "string",
            "description": "For set_value/set_property/disconnect: target node name."
          },
          "input": {
            "type": "string",
            "description": "For set_value: input socket name (e.g. 'Base Color', 'Metallic'). For disconnect: input socket to disconnect."
          },
          "value": {
            "description": "For set_value: the value to set. Type depends on the socket (number, array, string, boolean)."
          },
          "property": {
            "type": "string",
            "description": "For set_property: node property name (e.g. 'interpolation', 'blend_type', 'operation')."
          },
          "from_node": {
            "type": "string",
            "description": "For connect: source node name."
          },
          "from_socket": {
            "type": "string",
            "description": "For connect: source output socket name."
          },
          "to_node": {
            "type": "string",
            "description": "For connect: destination node name."
          },
          "to_socket": {
            "type": "string",
            "description": "For connect: destination input socket name."
          }
        },
        "required": ["action"]
      },
      "description": "Array of node operations to execute in order."
    }
  },
  "required": ["tree_type", "context", "operations"],
  "additionalProperties": false
}
```

**Internal mapping**: New node editor handler — operates on node_tree.nodes and node_tree.links

---

### 13. blender_edit_animation

**Description**: Edit animation data — insert/modify/delete keyframes, manage NLA strips, set drivers, control shape keys, and configure timeline settings. For reading animation data, use blender_get_animation_data.

**Annotations**: readOnly=false, destructive=false, idempotent=false

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["insert_keyframe", "delete_keyframe", "modify_keyframe", "add_nla_strip", "modify_nla_strip", "remove_nla_strip", "add_driver", "remove_driver", "set_shape_key", "set_frame", "set_frame_range"],
      "description": "The animation operation to perform."
    },
    "object_name": {
      "type": "string",
      "description": "Target object name."
    },
    "data_path": {
      "type": "string",
      "description": "Property path for keyframe/driver (e.g. 'location', 'rotation_euler', 'scale', 'energy', or custom paths like 'modifiers[\"Subsurf\"].levels')."
    },
    "index": {
      "type": "integer",
      "default": -1,
      "description": "Array index for the property (-1 for all channels, 0/1/2 for X/Y/Z)."
    },
    "frame": {
      "type": "integer",
      "description": "Frame number for keyframe operations."
    },
    "value": {
      "description": "Value for keyframe or shape key (number, array, or boolean)."
    },
    "interpolation": {
      "type": "string",
      "enum": ["CONSTANT", "LINEAR", "BEZIER", "SINE", "QUAD", "CUBIC", "QUART", "QUINT", "EXPO", "CIRC", "BACK", "BOUNCE", "ELASTIC"],
      "description": "Keyframe interpolation type."
    },
    "nla_action": {
      "type": "string",
      "description": "Action name for NLA strip operations."
    },
    "nla_start_frame": {
      "type": "integer",
      "description": "Start frame for NLA strip."
    },
    "nla_strip_name": {
      "type": "string",
      "description": "NLA strip name for modify/remove operations."
    },
    "driver_expression": {
      "type": "string",
      "description": "Python expression for driver (e.g. 'frame * 0.1', 'var + 5')."
    },
    "shape_key_name": {
      "type": "string",
      "description": "Shape key name for set_shape_key action."
    },
    "fps": {
      "type": "number",
      "description": "Frames per second (for set_frame_range)."
    },
    "frame_start": {
      "type": "integer",
      "description": "Start frame (for set_frame_range or set_frame)."
    },
    "frame_end": {
      "type": "integer",
      "description": "End frame (for set_frame_range)."
    }
  },
  "required": ["action"],
  "additionalProperties": false
}
```

**Internal mapping**: operator.execute(object.keyframe_insert/delete) + NLA API + driver API

---

### 14. blender_edit_sequencer

**Description**: Edit the Video Sequence Editor (VSE) — add/modify/delete strips, add transitions and effects. Supports video, image, audio, text, color, and adjustment layer strips. For compositing node-based post-processing, use blender_edit_nodes with tree_type=COMPOSITOR.

**Annotations**: readOnly=false, destructive=false, idempotent=false

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["add_strip", "modify_strip", "delete_strip", "add_effect", "add_transition", "move_strip"],
      "description": "The sequencer operation to perform."
    },
    "strip_type": {
      "type": "string",
      "enum": ["VIDEO", "IMAGE", "AUDIO", "TEXT", "COLOR", "ADJUSTMENT"],
      "description": "Type of strip to add (for add_strip action)."
    },
    "filepath": {
      "type": "string",
      "description": "File path for VIDEO/IMAGE/AUDIO strips."
    },
    "channel": {
      "type": "integer",
      "minimum": 1,
      "description": "VSE channel number."
    },
    "frame_start": {
      "type": "integer",
      "description": "Start frame of the strip."
    },
    "frame_end": {
      "type": "integer",
      "description": "End frame of the strip."
    },
    "strip_name": {
      "type": "string",
      "description": "Strip name for modify/delete/move operations."
    },
    "text": {
      "type": "string",
      "description": "Text content for TEXT strips."
    },
    "font_size": {
      "type": "number",
      "description": "Font size for TEXT strips."
    },
    "color": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 3,
      "maxItems": 4,
      "description": "Color [r,g,b] or [r,g,b,a] for TEXT/COLOR strips."
    },
    "effect_type": {
      "type": "string",
      "enum": ["TRANSFORM", "SPEED", "GLOW", "GAUSSIAN_BLUR", "COLOR_BALANCE", "ALPHA_OVER", "ALPHA_UNDER", "MULTIPLY"],
      "description": "Effect type for add_effect action."
    },
    "transition_type": {
      "type": "string",
      "enum": ["CROSS", "WIPE", "GAMMA_CROSS"],
      "description": "Transition type for add_transition action."
    },
    "transition_duration": {
      "type": "integer",
      "description": "Duration in frames for transitions."
    },
    "settings": {
      "type": "object",
      "description": "Additional settings specific to the strip/effect type."
    }
  },
  "required": ["action"],
  "additionalProperties": false
}
```

**Internal mapping**: New VSE handler — bpy.context.scene.sequence_editor API

---

## Imperative Write Layer (9 Tools)

### 15. blender_create_object

**Description**: Create a new object in the Blender scene. Supports mesh primitives, lights, cameras, curves, empties, armatures, and text objects. The object is automatically linked to the specified collection (or scene collection if omitted). Use blender_modify_object to change properties after creation. Use blender_manage_material to assign materials.

**Annotations**: readOnly=false, destructive=false, idempotent=false

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Name for the new object. Blender auto-suffixes if name already exists.",
      "maxLength": 63
    },
    "object_type": {
      "type": "string",
      "enum": ["MESH", "LIGHT", "CAMERA", "CURVE", "EMPTY", "ARMATURE", "TEXT"],
      "default": "MESH",
      "description": "Type of object to create."
    },
    "primitive": {
      "type": "string",
      "enum": ["cube", "sphere", "cylinder", "cone", "plane", "torus", "icosphere"],
      "description": "Mesh primitive shape. Only used when object_type=MESH."
    },
    "size": {
      "type": "number",
      "default": 2.0,
      "minimum": 0.001,
      "description": "Size of the mesh primitive in Blender units."
    },
    "segments": {
      "type": "integer",
      "default": 32,
      "minimum": 3,
      "description": "Number of segments for sphere/cylinder/cone/torus."
    },
    "light_type": {
      "type": "string",
      "enum": ["POINT", "SUN", "SPOT", "AREA"],
      "default": "POINT",
      "description": "Light type. Only used when object_type=LIGHT."
    },
    "energy": {
      "type": "number",
      "default": 1000,
      "description": "Light energy in watts. Only for LIGHT objects."
    },
    "color": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 3,
      "maxItems": 3,
      "description": "Light color [r,g,b] range 0-1. Only for LIGHT objects."
    },
    "lens": {
      "type": "number",
      "default": 50,
      "description": "Camera focal length in mm. Only for CAMERA objects."
    },
    "clip_start": {
      "type": "number",
      "default": 0.1,
      "description": "Camera near clip distance. Only for CAMERA objects."
    },
    "clip_end": {
      "type": "number",
      "default": 1000,
      "description": "Camera far clip distance. Only for CAMERA objects."
    },
    "set_active_camera": {
      "type": "boolean",
      "default": false,
      "description": "Set this camera as the active scene camera. Only for CAMERA objects."
    },
    "curve_type": {
      "type": "string",
      "enum": ["BEZIER", "NURBS", "POLY"],
      "default": "BEZIER",
      "description": "Spline type. Only for CURVE objects."
    },
    "body": {
      "type": "string",
      "description": "Text content. Only for TEXT objects."
    },
    "extrude": {
      "type": "number",
      "default": 0,
      "description": "Extrude depth for TEXT objects."
    },
    "location": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 3,
      "maxItems": 3,
      "default": [0, 0, 0],
      "description": "3D position [x, y, z]."
    },
    "rotation": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 3,
      "maxItems": 3,
      "default": [0, 0, 0],
      "description": "Euler rotation [x, y, z] in radians."
    },
    "scale": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 3,
      "maxItems": 3,
      "default": [1, 1, 1],
      "description": "Scale [x, y, z]."
    },
    "collection": {
      "type": "string",
      "description": "Collection to link to. Uses scene collection if omitted."
    }
  },
  "required": ["name"],
  "additionalProperties": false
}
```

**Internal mapping**: ObjectHandler.create + MeshHandler/LightHandler/CameraHandler/CurveHandler/FontHandler based on object_type

---

### 16. blender_modify_object

**Description**: Modify an existing object's properties — transform (location/rotation/scale), parent-child relationships, visibility, rename, set origin, or delete. Use blender_manage_modifier for modifiers, blender_manage_material for materials, blender_manage_constraints for constraints.

**Annotations**: readOnly=false, destructive=varies (true when delete=true), idempotent=true (except delete)

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Name of the object to modify."
    },
    "location": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 3,
      "maxItems": 3,
      "description": "New 3D position [x, y, z]."
    },
    "rotation": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 3,
      "maxItems": 3,
      "description": "New Euler rotation [x, y, z] in radians."
    },
    "scale": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 3,
      "maxItems": 3,
      "description": "New scale [x, y, z]."
    },
    "parent": {
      "type": "string",
      "description": "Name of parent object. Set to '' to clear parent."
    },
    "visible": {
      "type": "boolean",
      "description": "Viewport visibility."
    },
    "hide_render": {
      "type": "boolean",
      "description": "Hide from render."
    },
    "new_name": {
      "type": "string",
      "description": "Rename the object.",
      "maxLength": 63
    },
    "active": {
      "type": "boolean",
      "description": "Set as active object."
    },
    "selected": {
      "type": "boolean",
      "description": "Set selection state."
    },
    "origin": {
      "type": "string",
      "enum": ["GEOMETRY", "CURSOR", "MEDIAN"],
      "description": "Set origin to geometry center, 3D cursor, or median point."
    },
    "delete": {
      "type": "boolean",
      "default": false,
      "description": "If true, delete this object from the scene."
    },
    "delete_data": {
      "type": "boolean",
      "default": true,
      "description": "When deleting, also delete the underlying data block (mesh, curve, etc.)."
    }
  },
  "required": ["name"],
  "additionalProperties": false
}
```

**Internal mapping**: ObjectHandler.write / ObjectHandler.delete

---

### 17. blender_manage_material

**Description**: Create, edit, assign, duplicate, or delete materials. For high-level PBR property editing only. For node-level shader editing, use blender_edit_nodes with tree_type=SHADER.

**Annotations**: readOnly=false, destructive=varies, idempotent=varies

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["create", "edit", "assign", "unassign", "duplicate", "delete"],
      "description": "The material operation to perform."
    },
    "name": {
      "type": "string",
      "description": "Material name. For create: desired name. For edit/assign/duplicate/delete: existing material name."
    },
    "base_color": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 4,
      "maxItems": 4,
      "description": "Base color [r,g,b,a] range 0-1. For create/edit."
    },
    "metallic": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Metallic value 0-1. For create/edit."
    },
    "roughness": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Roughness value 0-1. For create/edit."
    },
    "specular": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Specular value 0-1. For create/edit."
    },
    "alpha": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Alpha value 0-1. For create/edit."
    },
    "emission_color": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 4,
      "maxItems": 4,
      "description": "Emission color [r,g,b,a]. For create/edit."
    },
    "emission_strength": {
      "type": "number",
      "description": "Emission strength. For create/edit."
    },
    "use_fake_user": {
      "type": "boolean",
      "description": "If true, material won't be auto-deleted when unused. Enables reuse across saves."
    },
    "object_name": {
      "type": "string",
      "description": "Object name for assign/unassign actions."
    },
    "slot": {
      "type": "integer",
      "minimum": 0,
      "description": "Material slot index for assign/unassign. 0-based."
    }
  },
  "required": ["action", "name"],
  "additionalProperties": false
}
```

**Internal mapping**: MaterialHandler.create/write/link/delete

---

### 18. blender_manage_modifier

**Description**: Add, configure, apply, remove, or reorder modifiers on an object. For reading modifier details, use blender_get_object_data with include=["modifiers"].

**Annotations**: readOnly=false, destructive=varies (apply/remove), idempotent=varies

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["add", "configure", "apply", "remove", "move_up", "move_down"],
      "description": "The modifier operation to perform."
    },
    "object_name": {
      "type": "string",
      "description": "Name of the object."
    },
    "modifier_name": {
      "type": "string",
      "description": "Name of the modifier. For add: desired name. For configure/apply/remove/move: existing name."
    },
    "modifier_type": {
      "type": "string",
      "enum": ["SUBSURF", "MIRROR", "ARRAY", "BOOLEAN", "SOLIDIFY", "BEVEL", "SHRINKWRAP", "DECIMATE", "REMESH", "WEIGHTED_NORMAL", "SIMPLE_DEFORM", "SKIN", "WIREFRAME", "SCREW", "DISPLACE", "CAST", "SMOOTH", "LAPLACIANSMOOTH", "CORRECTIVE_SMOOTH", "CURVE", "LATTICE", "WARP", "WAVE", "CLOTH", "COLLISION", "ARMATURE", "MESH_DEFORM", "HOOK", "SURFACE_DEFORM", "DATA_TRANSFER", "NORMAL_EDIT", "UV_PROJECT", "UV_WARP", "VERTEX_WEIGHT_EDIT", "VERTEX_WEIGHT_MIX", "VERTEX_WEIGHT_PROXIMITY", "NODES"],
      "description": "Modifier type. For add action only."
    },
    "settings": {
      "type": "object",
      "description": "Modifier settings as key-value pairs (e.g. {\"levels\": 3, \"render_levels\": 4} for SUBSURF)."
    }
  },
  "required": ["action", "object_name"],
  "additionalProperties": false
}
```

**Internal mapping**: ModifierHandler.create/write/delete + operator.execute(object.modifier_apply/move_up/move_down)

---

### 19. blender_manage_collection

**Description**: Create, delete, or manage collections — link/unlink objects, set parent collection, control visibility, set color tags. For reading collection data, use blender_get_collections.

**Annotations**: readOnly=false, destructive=varies, idempotent=varies

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["create", "delete", "link_object", "unlink_object", "set_visibility", "set_parent"],
      "description": "The collection operation to perform."
    },
    "collection_name": {
      "type": "string",
      "description": "Name of the collection."
    },
    "object_name": {
      "type": "string",
      "description": "Object name for link/unlink operations."
    },
    "parent": {
      "type": "string",
      "description": "Parent collection name. For create: where to nest. For set_parent: new parent."
    },
    "hide_viewport": {
      "type": "boolean",
      "description": "Hide collection in viewport (for set_visibility)."
    },
    "hide_render": {
      "type": "boolean",
      "description": "Hide collection in render (for set_visibility)."
    },
    "color_tag": {
      "type": "string",
      "enum": ["NONE", "COLOR_01", "COLOR_02", "COLOR_03", "COLOR_04", "COLOR_05", "COLOR_06", "COLOR_07", "COLOR_08"],
      "description": "Color tag for visual organization."
    }
  },
  "required": ["action", "collection_name"],
  "additionalProperties": false
}
```

**Internal mapping**: CollectionHandler.create/delete/link + layer collection visibility

---

### 20. blender_manage_uv

**Description**: UV mapping operations — mark/clear seams, unwrap with various algorithms, pack/scale UV islands, manage UV layers. This handles the algorithmic/parametric side of UV work. For UV painting (spatial brush operations), use blender_execute_operator.

**Annotations**: readOnly=false, destructive=false, idempotent=varies

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["mark_seam", "clear_seam", "unwrap", "smart_project", "cube_project", "cylinder_project", "sphere_project", "lightmap_pack", "pack_islands", "average_island_scale", "add_uv_map", "remove_uv_map", "set_active_uv"],
      "description": "The UV operation to perform."
    },
    "object_name": {
      "type": "string",
      "description": "Name of the mesh object."
    },
    "uv_map_name": {
      "type": "string",
      "description": "UV map name for add/remove/set_active operations."
    },
    "angle_limit": {
      "type": "number",
      "default": 66.0,
      "minimum": 0,
      "maximum": 89,
      "description": "Angle limit in degrees for smart_project."
    },
    "island_margin": {
      "type": "number",
      "default": 0.02,
      "minimum": 0,
      "maximum": 1,
      "description": "Margin between UV islands for pack_islands and smart_project."
    },
    "correct_aspect": {
      "type": "boolean",
      "default": true,
      "description": "Correct for non-square textures in UV projection."
    },
    "selection_mode": {
      "type": "string",
      "enum": ["SHARP_EDGES", "ANGLE_BASED", "ALL_EDGES"],
      "description": "Auto-select edges for mark_seam. SHARP_EDGES uses auto smooth angle, ANGLE_BASED uses angle_limit."
    }
  },
  "required": ["action", "object_name"],
  "additionalProperties": false
}
```

**Internal mapping**: New UV handler — wraps bpy.ops.uv.* and bpy.ops.mesh.mark_seam operators

---

### 21. blender_manage_constraints

**Description**: Add, configure, remove, enable/disable, or reorder constraints on objects or bones. Constraints are fundamental for rigging, animation, and motion control. For reading constraint data, use blender_get_object_data with include=["constraints"] or blender_get_armature_data with include=["constraints"].

**Annotations**: readOnly=false, destructive=varies, idempotent=varies

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["add", "configure", "remove", "enable", "disable", "move_up", "move_down"],
      "description": "The constraint operation to perform."
    },
    "target_type": {
      "type": "string",
      "enum": ["OBJECT", "BONE"],
      "default": "OBJECT",
      "description": "Whether the constraint is on an object or a bone."
    },
    "target_name": {
      "type": "string",
      "description": "Object name for OBJECT constraints. Format 'ArmatureName/BoneName' for BONE constraints."
    },
    "constraint_name": {
      "type": "string",
      "description": "Constraint name. For add: desired name. For configure/remove/enable/disable: existing name."
    },
    "constraint_type": {
      "type": "string",
      "enum": ["COPY_LOCATION", "COPY_ROTATION", "COPY_SCALE", "COPY_TRANSFORMS", "LIMIT_DISTANCE", "LIMIT_LOCATION", "LIMIT_ROTATION", "LIMIT_SCALE", "TRACK_TO", "DAMPED_TRACK", "LOCKED_TRACK", "IK", "STRETCH_TO", "FLOOR", "CHILD_OF", "FOLLOW_PATH", "CLAMP_TO", "PIVOT", "MAINTAIN_VOLUME", "TRANSFORMATION", "SHRINKWRAP", "ACTION"],
      "description": "Constraint type for add action."
    },
    "settings": {
      "type": "object",
      "description": "Constraint settings as key-value pairs (e.g. {\"target\": \"Empty\", \"influence\": 0.5, \"track_axis\": \"TRACK_NEGATIVE_Z\"})."
    }
  },
  "required": ["action", "target_name"],
  "additionalProperties": false
}
```

**Internal mapping**: New constraint handler — bpy.context.object.constraints API + bone constraints

---

### 22. blender_manage_physics

**Description**: Add, configure, remove, or bake physics simulations on objects — rigid body, cloth, soft body, fluid, particle systems, and force fields. For reading physics data, use blender_get_object_data with include=["physics"].

**Annotations**: readOnly=false, destructive=false, idempotent=varies

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["add", "configure", "remove", "bake", "free_bake"],
      "description": "The physics operation to perform."
    },
    "object_name": {
      "type": "string",
      "description": "Name of the object."
    },
    "physics_type": {
      "type": "string",
      "enum": ["RIGID_BODY", "RIGID_BODY_PASSIVE", "CLOTH", "SOFT_BODY", "FLUID_DOMAIN", "FLUID_FLOW", "PARTICLE", "FORCE_FIELD"],
      "description": "Physics type for add action."
    },
    "force_field_type": {
      "type": "string",
      "enum": ["WIND", "TURBULENCE", "VORTEX", "MAGNETIC", "HARMONIC", "CHARGE", "DRAG", "FORCE"],
      "description": "Force field type. Only for physics_type=FORCE_FIELD."
    },
    "settings": {
      "type": "object",
      "description": "Physics settings as key-value pairs (e.g. {\"mass\": 5, \"friction\": 0.5} for RIGID_BODY, {\"count\": 5000, \"lifetime\": 50} for PARTICLE)."
    },
    "frame_start": {
      "type": "integer",
      "description": "Bake start frame."
    },
    "frame_end": {
      "type": "integer",
      "description": "Bake end frame."
    }
  },
  "required": ["action", "object_name"],
  "additionalProperties": false
}
```

**Internal mapping**: New physics handler — bpy.ops.rigidbody/cloth/particle + bpy.ops.ptcache

---

### 23. blender_setup_scene

**Description**: Configure scene-level settings — render engine and quality, output resolution and format, world environment basics, and timeline/FPS. For detailed world shader editing, use blender_edit_nodes with tree_type=SHADER, context=WORLD.

**Annotations**: readOnly=false, destructive=false, idempotent=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "engine": {
      "type": "string",
      "enum": ["BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES"],
      "description": "Render engine."
    },
    "samples": {
      "type": "integer",
      "minimum": 1,
      "description": "Render samples."
    },
    "resolution_x": {
      "type": "integer",
      "minimum": 1,
      "description": "Output width in pixels."
    },
    "resolution_y": {
      "type": "integer",
      "minimum": 1,
      "description": "Output height in pixels."
    },
    "output_format": {
      "type": "string",
      "enum": ["PNG", "JPEG", "OPEN_EXR", "TIFF", "BMP", "FFMPEG"],
      "description": "Output file format."
    },
    "output_path": {
      "type": "string",
      "description": "Output file/directory path."
    },
    "film_transparent": {
      "type": "boolean",
      "description": "Render with transparent background."
    },
    "denoising": {
      "type": "boolean",
      "description": "Enable render denoising."
    },
    "denoiser": {
      "type": "string",
      "enum": ["OPTIX", "OPENIMAGEDENOISE"],
      "description": "Denoiser type (requires denoising=true)."
    },
    "background_color": {
      "type": "array",
      "items": {"type": "number"},
      "minItems": 4,
      "maxItems": 4,
      "description": "World background color [r,g,b,a]."
    },
    "background_strength": {
      "type": "number",
      "description": "World background strength."
    },
    "fps": {
      "type": "number",
      "description": "Frames per second."
    },
    "frame_start": {
      "type": "integer",
      "description": "Scene start frame."
    },
    "frame_end": {
      "type": "integer",
      "description": "Scene end frame."
    },
    "frame_current": {
      "type": "integer",
      "description": "Set current frame."
    }
  },
  "additionalProperties": false
}
```

**Internal mapping**: bpy.context.scene.render + bpy.context.scene.world + bpy.context.scene frame properties

---

## Fallback Layer (3 Tools)

### 24. blender_execute_operator

**Description**: Execute any Blender operator (bpy.ops.*). This is the escape hatch for operations not covered by specialized tools — UV painting, sculpting, physics baking, file operations, and 1000+ other Blender operators. Use specialized tools first when available.

**Annotations**: readOnly=false, destructive=false, idempotent=false

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "operator": {
      "type": "string",
      "description": "Operator identifier in 'category.name' format (e.g. 'mesh.primitive_cube_add', 'uv.smart_project', 'object.voxel_remesh')."
    },
    "params": {
      "type": "object",
      "description": "Operator parameters as key-value pairs."
    },
    "context": {
      "type": "object",
      "description": "Context override dictionary (e.g. {\"active_object\": \"Cube\", \"mode\": \"EDIT\"})."
    }
  },
  "required": ["operator"],
  "additionalProperties": false
}
```

**Internal mapping**: operator_execute (existing handler)

---

### 25. blender_execute_script

**Description**: Execute arbitrary Python code in Blender's Python environment. This is the ultimate fallback for operations that cannot be expressed through any other tool. Use with caution — this tool has full access to Blender's API and filesystem.

**Annotations**: readOnly=false, destructive=true, idempotent=false

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "code": {
      "type": "string",
      "description": "Python code to execute. Has access to bpy, mathutils, and all Blender modules."
    }
  },
  "required": ["code"],
  "additionalProperties": false
}
```

**Internal mapping**: script_execute (existing handler, default disabled)

---

### 26. blender_import_export

**Description**: Import or export asset files in various formats. For FBX, OBJ, glTF, USD, Alembic, STL, and more.

**Annotations**: readOnly=false, destructive=false, idempotent=false, openWorld=true

**inputSchema**:
```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["import", "export"],
      "description": "Whether to import or export."
    },
    "format": {
      "type": "string",
      "enum": ["FBX", "OBJ", "GLTF", "GLB", "USD", "USDC", "USDA", "ALEMBIC", "STL", "PLY", "SVG", "DAE", "X3D"],
      "description": "File format."
    },
    "filepath": {
      "type": "string",
      "description": "Absolute file path for import source or export destination."
    },
    "settings": {
      "type": "object",
      "description": "Format-specific settings (e.g. {\"use_selection\": true} for FBX export, {\"export_draco_mesh_compression_enable\": true} for glTF)."
    }
  },
  "required": ["action", "format", "filepath"],
  "additionalProperties": false
}
```

**Internal mapping**: operator.execute with format-specific import/export operators

---

## Handler Mapping Summary

| Tool | Existing Handler | New Handler Needed |
|------|-----------------|-------------------|
| get_objects | ObjectHandler.list_items | — |
| get_object_data | ObjectHandler.read + type handlers | Extend include logic |
| get_node_tree | — | ✅ NodeTreeReader |
| get_animation_data | info_query partial | ✅ AnimationReader |
| get_materials | MaterialHandler.list_items | — |
| get_scene | info_query | Extend |
| get_collections | CollectionHandler.read | Extend recursion |
| get_armature_data | ArmatureHandler.read | ✅ Extend bone iteration |
| get_images | — | ✅ ImageReader |
| capture_viewport | info_query(viewport_capture) | Extend params |
| get_selection | info_query(selection+mode) | — |
| edit_nodes | — | ✅ NodeTreeEditor |
| edit_animation | — | ✅ AnimationEditor |
| edit_sequencer | — | ✅ SequencerEditor |
| create_object | ObjectHandler.create + type handlers | Compose existing |
| modify_object | ObjectHandler.write/delete | — |
| manage_material | MaterialHandler.create/write/link/delete | — |
| manage_modifier | ModifierHandler.create/write/delete | Add apply/move |
| manage_collection | CollectionHandler.create/delete/link | — |
| manage_uv | — | ✅ UVHandler |
| manage_constraints | — | ✅ ConstraintHandler |
| manage_physics | — | ✅ PhysicsHandler |
| setup_scene | — | ✅ SceneConfigHandler |
| execute_operator | operator_execute | — |
| execute_script | script_execute | — |
| import_export | operator_execute | Schema mapping layer |

**Existing handlers reused**: 16 tools
**New handlers needed**: 10 tools (NodeTreeReader, NodeTreeEditor, AnimationReader, AnimationEditor, SequencerEditor, ImageReader, UVHandler, ConstraintHandler, PhysicsHandler, SceneConfigHandler)

---

## Tool Annotations

### Standard MCP Annotations

All 26 tools carry these annotations (defined by MCP spec as "untrusted hints"):

| Annotation | Type | Purpose |
|------------|------|---------|
| `title` | string | Human-readable display name |
| `readOnlyHint` | boolean | Tool does not modify Blender state |
| `destructiveHint` | boolean | Tool may make irreversible changes |
| `idempotentHint` | boolean | Repeated calls with same args produce same result |
| `openWorldHint` | boolean | Tool accesses external network |

### Annotation Mapping

| Tool | readOnly | destructive | idempotent | openWorld |
|------|----------|-------------|------------|-----------|
| **Perception (11)** | | | | |
| blender_get_objects | true | false | true | false |
| blender_get_object_data | true | false | true | false |
| blender_get_node_tree | true | false | true | false |
| blender_get_animation_data | true | false | true | false |
| blender_get_materials | true | false | true | false |
| blender_get_scene | true | false | true | false |
| blender_get_collections | true | false | true | false |
| blender_get_armature_data | true | false | true | false |
| blender_get_images | true | false | true | false |
| blender_capture_viewport | true | false | true | false |
| blender_get_selection | true | false | true | false |
| **Declarative Write (3)** | | | | |
| blender_edit_nodes | false | false | false | false |
| blender_edit_animation | false | false | false | false |
| blender_edit_sequencer | false | false | false | false |
| **Imperative Write (9)** | | | | |
| blender_create_object | false | false | false | false |
| blender_modify_object | false | false | false | false |
| blender_manage_material | false | false | false | false |
| blender_manage_modifier | false | false | false | false |
| blender_manage_collection | false | false | false | false |
| blender_manage_uv | false | false | false | false |
| blender_manage_constraints | false | false | false | false |
| blender_manage_physics | false | false | false | false |
| blender_setup_scene | false | false | true | false |
| **Fallback (3)** | | | | |
| blender_execute_operator | false | false | false | false |
| blender_execute_script | false | true | false | false |
| blender_import_export | false | false | false | true |

### Dynamic Annotation Strategy

Tools with `action` parameters (e.g., manage_material has create/edit/delete) contain both safe and destructive actions. Since MCP annotations are static per-tool:

1. **Static annotations use conservative values** — destructive=false for tools that are only sometimes destructive.
2. **Description text clarifies** — "The 'delete' action is destructive and irreversible." LLMs understand natural language better than boolean flags.

---

## Tool Description Convention

### Three-Part Template

Every tool description follows this structure:

```
[WHAT] One sentence stating what the tool does.
[WHEN] When to use this tool (trigger conditions).
[NOT]  When NOT to use it, with cross-references to the correct tool.
```

### Cross-Reference Matrix (Key Paths)

Tools that LLMs commonly confuse are explicitly disambiguated in their descriptions:

```
blender_get_object_data →
  "For armature bone hierarchy/poses/constraints, use blender_get_armature_data."
  "For node tree structure, use blender_get_node_tree."

blender_edit_nodes →
  "For high-level PBR properties (base_color, metallic, roughness),
   use blender_manage_material. For reading node trees first,
   use blender_get_node_tree."

blender_manage_material →
  "For node-level shader editing (adding/connecting shader nodes),
   use blender_edit_nodes with tree_type=SHADER, context=OBJECT."

blender_modify_object →
  "For modifiers: blender_manage_modifier.
   For materials: blender_manage_material.
   For constraints: blender_manage_constraints.
   For physics: blender_manage_physics."

blender_setup_scene →
  "For detailed world shader node editing (HDRI setup, complex environment),
   use blender_edit_nodes with tree_type=SHADER, context=WORLD."

blender_execute_operator →
  "Escape hatch for operations without a dedicated tool. Always prefer
   specialized tools: blender_manage_uv for UV, blender_manage_modifier
   for modifiers, blender_manage_physics for physics, etc."

blender_execute_script →
  "Ultimate fallback. Use only when no other tool can accomplish the task.
   Try blender_execute_operator first for standard Blender operations."

blender_import_export →
  "For importing/exporting files only. For scene manipulation,
   use blender_create_object or blender_modify_object."
```

### Parameter Description Rules

| Rule | Bad | Good |
|------|-----|------|
| State meaning, not just type | `"type": "number"` | `"Metallic value 0-1. 0=dielectric, 1=full metal"` |
| Always list enum values | (omitted) | `"enum": ["POINT","SUN","SPOT","AREA"]` |
| Include default in text | (omitted) | `"Size in Blender units (default: 2.0)"` |
| Specify units | `"Rotation values"` | `"Euler rotation [x,y,z] in radians"` |
| Give format examples | `"Operator name"` | `"Operator ID in 'category.name' format (e.g. 'mesh.primitive_cube_add')"` |
| Explicit array constraints | `"type": "array"` | `"minItems": 3, "maxItems": 3` + `"3D position [x,y,z]"` |

---

## MCP Prompts (Workflow Guidance)

### Role of Prompts

```
Tools = Vocabulary (what each word means)
Prompts = Grammar (how words compose into sentences)
```

- **Tools** teach LLM "how to use each individual tool" via description + schema.
- **Prompts** teach LLM "how to combine tools into workflows" via step-by-step templates.
- Prompts are **user-controlled** (triggered via /slash-command), not auto-invoked by LLM.

### Three-Layer Guidance System

| Layer | Content | Audience | Injection |
|-------|---------|----------|-----------|
| Schema | JSON Schema constraints (enum, default, required) | LLM + client validator | Always (tool registration) |
| Description | WHAT/WHEN/NOT + cross-references | LLM | Always (tool listing) |
| Prompt | Multi-tool workflow steps with examples | LLM | On user /command trigger |

### Prompt Registry (7 Core Prompts)

#### 1. blender-scene-setup

**Description**: Guide through creating a new scene with camera, lighting, and world setup.

**Arguments**: `style` (realistic/stylized/architectural), `resolution` (1080p/4K/square)

**Workflow**:
1. `blender_get_scene` — Survey current state
2. `blender_setup_scene` — Set engine, resolution, samples
3. `blender_create_object(CAMERA)` — Set up camera with lens and position
4. `blender_create_object(LIGHT)` — Set up lighting (3-point for realistic, single sun for stylized)
5. `blender_edit_nodes(SHADER/WORLD)` — Configure world environment (HDRI or gradient)
6. `blender_capture_viewport(RENDERED)` — Visual verification

---

#### 2. blender-material-create

**Description**: Guide through creating and assigning a PBR material.

**Arguments**: `material_type` (metal/glass/wood/fabric/emissive/custom), `target_object`

**Workflow**:
1. `blender_get_materials` — Check for existing reusable materials
2. `blender_manage_material(create)` — Create with PBR preset values
3. `blender_edit_nodes(SHADER/OBJECT)` — Add complexity (textures, normal maps, effects)
4. `blender_manage_material(assign)` — Assign to target object
5. `blender_capture_viewport(MATERIAL)` — Preview result

---

#### 3. blender-model-asset

**Description**: Guide through creating a mesh asset with modifiers and organization.

**Arguments**: `description` (what to model), `complexity` (simple/moderate/complex)

**Workflow**:
1. `blender_get_objects` — Check existing scene
2. `blender_create_object(MESH)` — Start with appropriate primitive
3. `blender_manage_modifier` — Add modifiers (mirror, subsurf, bevel)
4. `blender_manage_collection` — Organize into collection
5. `blender_manage_material` — Assign material
6. `blender_manage_uv(smart_project)` — UV unwrap for texturing
7. `blender_capture_viewport(SOLID)` — Verify topology

---

#### 4. blender-animate

**Description**: Guide through creating animation on objects.

**Arguments**: `animation_type` (transform/camera/character/physics), `target`

**Workflow**:
1. `blender_get_animation_data` — Check existing animation
2. `blender_setup_scene` — Set frame range and FPS
3. `blender_edit_animation(insert_keyframe)` — Create keyframes
4. `blender_edit_animation(modify_keyframe)` — Adjust interpolation curves
5. (Optional) `blender_edit_animation(add_nla_strip)` — Sequence multiple actions
6. `blender_capture_viewport` — Preview at key frames

---

#### 5. blender-composite

**Description**: Guide through setting up compositor post-processing effects.

**Arguments**: `effects` (glow/color-grade/vignette/depth-of-field/custom)

**Workflow**:
1. `blender_get_node_tree(COMPOSITOR/SCENE)` — Check current compositor setup
2. `blender_edit_nodes(COMPOSITOR/SCENE)` — Add effect nodes (Glare, Color Balance, Lens Distortion, etc.)
3. `blender_capture_viewport(RENDERED)` — Preview result

---

#### 6. blender-render-output

**Description**: Guide through configuring and executing a final render.

**Arguments**: `output_type` (still/animation/turntable)

**Workflow**:
1. `blender_get_scene(include=["render","timeline"])` — Check render config
2. `blender_setup_scene` — Adjust render settings if needed
3. `blender_capture_viewport(camera_view=true, shading=RENDERED)` — Final preview
4. `blender_execute_operator("render.render")` — Execute render

---

#### 7. blender-diagnose

**Description**: Diagnose issues in a Blender scene with a systematic checklist.

**Arguments**: none

**Workflow**:
1. `blender_get_scene(include=["stats","render","world","version"])` — Scene overview
2. `blender_get_objects` — List all objects
3. `blender_get_selection` — Current context
4. `blender_capture_viewport(RENDERED)` — Visual check
5. `blender_get_materials(filter="all")` — Material audit
6. `blender_get_images(filter="missing")` — Find broken texture paths
7. Report findings with severity and recommended fixes

---

### Prompt Implementation

```python
# src/blender_mcp/prompts/registry.py

BLENDER_PROMPTS = {
    "blender-scene-setup": {
        "name": "blender-scene-setup",
        "title": "Set Up Blender Scene",
        "description": "Guide through creating a new scene with camera, lighting, and world setup.",
        "arguments": [
            {"name": "style", "description": "Rendering style: realistic, stylized, or architectural", "required": True},
            {"name": "resolution", "description": "Output resolution: 1080p, 4K, or square", "required": False}
        ]
    },
    "blender-material-create": {
        "name": "blender-material-create",
        "title": "Create Material",
        "description": "Guide through creating and assigning a PBR material.",
        "arguments": [
            {"name": "material_type", "description": "metal, glass, wood, fabric, emissive, custom", "required": True},
            {"name": "target_object", "description": "Object to assign the material to", "required": True}
        ]
    },
    "blender-model-asset": {
        "name": "blender-model-asset",
        "title": "Create Model Asset",
        "description": "Guide through creating a mesh asset with modifiers and organization.",
        "arguments": [
            {"name": "description", "description": "What to model", "required": True},
            {"name": "complexity", "description": "simple, moderate, or complex", "required": False}
        ]
    },
    "blender-animate": {
        "name": "blender-animate",
        "title": "Create Animation",
        "description": "Guide through creating animation on objects.",
        "arguments": [
            {"name": "animation_type", "description": "transform, camera, character, or physics", "required": True},
            {"name": "target", "description": "Object to animate", "required": True}
        ]
    },
    "blender-composite": {
        "name": "blender-composite",
        "title": "Set Up Compositing",
        "description": "Guide through compositor post-processing effects.",
        "arguments": [
            {"name": "effects", "description": "glow, color-grade, vignette, depth-of-field, or custom", "required": True}
        ]
    },
    "blender-render-output": {
        "name": "blender-render-output",
        "title": "Render Output",
        "description": "Guide through configuring and executing a final render.",
        "arguments": [
            {"name": "output_type", "description": "still, animation, or turntable", "required": True}
        ]
    },
    "blender-diagnose": {
        "name": "blender-diagnose",
        "title": "Diagnose Scene Issues",
        "description": "Systematically diagnose issues in a Blender scene.",
        "arguments": []
    }
}
```

### Prompt Message Generation

Each prompt handler returns a `GetPromptResult` with structured messages that:

1. Set the context (what the user wants to achieve)
2. List the step-by-step workflow with specific tool names
3. Include parameter examples for each step
4. End with a verification step (usually `blender_capture_viewport`)

The prompt messages use `role="user"` to inject the workflow template into the conversation, guiding the LLM's subsequent tool calls.
