# -*- coding: utf-8 -*-
"""All 26 tool definitions for Blender MCP.

Each tool definition contains:
- name: Tool name with blender_ prefix
- description: Three-part description (WHAT/WHEN/NOT)
- inputSchema: Hand-written JSON Schema with enum constraints
- annotations: MCP tool annotations (readOnlyHint, destructiveHint, etc.)
- internal: Internal routing info (capability name + param transform)
"""

from __future__ import annotations

from typing import Any


def _tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    annotations: dict[str, Any],
    internal_capability: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "inputSchema": input_schema,
        "annotations": annotations,
        "internal_capability": internal_capability,
    }


# ---------------------------------------------------------------------------
# Shared schema fragments
# ---------------------------------------------------------------------------


def _vec3(description: str, **kwargs: Any) -> dict[str, Any]:
    """Schema for a 3-element numeric array (e.g. location, rotation, scale)."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {"type": "number"},
        "minItems": 3,
        "maxItems": 3,
        "description": description,
    }
    schema.update(kwargs)
    return schema


def _rgba4(description: str, **kwargs: Any) -> dict[str, Any]:
    """Schema for a 4-element RGBA color array."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {"type": "number"},
        "minItems": 4,
        "maxItems": 4,
        "description": description,
    }
    schema.update(kwargs)
    return schema


def _color3_4(description: str, **kwargs: Any) -> dict[str, Any]:
    """Schema for a 3-or-4-element color array (RGB or RGBA)."""
    schema: dict[str, Any] = {
        "type": "array",
        "items": {"type": "number"},
        "minItems": 3,
        "maxItems": 4,
        "description": description,
    }
    schema.update(kwargs)
    return schema


# ---------------------------------------------------------------------------
# Perception Layer (11 Tools)
# ---------------------------------------------------------------------------

_PERCEPTION_TOOLS = [
    _tool(
        name="blender_get_objects",
        description=(
            "List objects in the Blender scene with optional filters. "
            "Returns name, type, location, and collection for each object.\n\n"
            "Use this as the first call to understand what exists in a scene.\n\n"
            "Do NOT use for: detailed object properties (use blender_get_object_data), "
            "material listing (use blender_get_materials), or collection tree (use blender_get_collections)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "type_filter": {
                    "type": "string",
                    "enum": [
                        "MESH",
                        "LIGHT",
                        "CAMERA",
                        "CURVE",
                        "EMPTY",
                        "ARMATURE",
                        "LATTICE",
                        "FONT",
                        "GPENCIL",
                        "SPEAKER",
                        "VOLUME",
                    ],
                    "description": "Filter by object type.",
                },
                "collection": {
                    "type": "string",
                    "description": "Filter by collection name. Only returns objects in this collection.",
                },
                "selected_only": {
                    "type": "boolean",
                    "default": False,
                    "description": "If true, only return currently selected objects.",
                },
                "visible_only": {
                    "type": "boolean",
                    "default": False,
                    "description": "If true, only return objects visible in viewport.",
                },
                "name_pattern": {
                    "type": "string",
                    "description": "Glob pattern to filter by name (e.g. 'SM_*' or '*_high').",
                },
            },
            "additionalProperties": False,
        },
        annotations={
            "title": "List Scene Objects",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.get_objects",
    ),
    _tool(
        name="blender_get_object_data",
        description=(
            "Get detailed data for a single object. Use the 'include' parameter to control "
            "which data is returned, avoiding context overflow.\n\n"
            "Use this when: you need details about a specific object.\n\n"
            "Do NOT use for: armature bone data (use blender_get_armature_data), "
            "node tree structure (use blender_get_node_tree)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the object to inspect.",
                },
                "include": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "summary",
                            "mesh_stats",
                            "modifiers",
                            "materials",
                            "constraints",
                            "physics",
                            "animation",
                            "custom_properties",
                            "vertex_groups",
                            "shape_keys",
                            "uv_maps",
                            "particle_systems",
                        ],
                    },
                    "default": ["summary"],
                    "description": "Which data sections to include. Use 'summary' for a quick overview.",
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Get Object Details",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.get_object_data",
    ),
    _tool(
        name="blender_get_node_tree",
        description=(
            "Read the structure of any node tree in Blender — shader nodes, compositor nodes, "
            "or geometry nodes. Returns nodes and links. Supports all 6 node tree contexts.\n\n"
            "Use this when: you need to understand a material's shader setup, compositor pipeline, "
            "or geometry nodes graph before editing.\n\n"
            "Do NOT use for: editing nodes (use blender_edit_nodes)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "tree_type": {
                    "type": "string",
                    "enum": ["SHADER", "COMPOSITOR", "GEOMETRY"],
                    "description": "Type of node tree to read.",
                },
                "context": {
                    "type": "string",
                    "enum": ["OBJECT", "WORLD", "LINESTYLE", "SCENE", "MODIFIER", "TOOL"],
                    "description": (
                        "Context within the tree type. "
                        "SHADER: OBJECT|WORLD|LINESTYLE. "
                        "COMPOSITOR: SCENE. "
                        "GEOMETRY: MODIFIER|TOOL."
                    ),
                },
                "target": {
                    "type": "string",
                    "description": (
                        "Target name. For SHADER/OBJECT: material name. "
                        "For SHADER/WORLD: world name. "
                        "For GEOMETRY/MODIFIER: 'ObjectName/ModifierName'."
                    ),
                },
                "depth": {
                    "type": "string",
                    "enum": ["summary", "full"],
                    "default": "summary",
                    "description": (
                        "Level of detail. 'summary' returns node names and types only. "
                        "'full' returns all parameters and connections."
                    ),
                },
            },
            "required": ["tree_type", "context"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Read Node Tree",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.get_node_tree",
    ),
    _tool(
        name="blender_get_animation_data",
        description=(
            "Read animation data for an object or scene — keyframes, F-Curves, NLA strips, "
            "drivers, and shape keys.\n\n"
            "Use this when: you need to understand existing animation before modifying it.\n\n"
            "Do NOT use for: modifying animation (use blender_edit_animation)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Object name, or 'scene' for scene-level animation data.",
                },
                "include": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["keyframes", "fcurves", "nla", "drivers", "shape_keys"],
                    },
                    "default": ["keyframes"],
                    "description": "Which animation data to include.",
                },
                "frame_range": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Optional [start, end] frame range to limit keyframe data.",
                },
            },
            "required": ["target"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Read Animation Data",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.get_animation_data",
    ),
    _tool(
        name="blender_get_materials",
        description=(
            "List all materials in the file with their basic properties (name, use_nodes, "
            "user count, base PBR values).\n\n"
            "Use this when: you need an overview of available materials.\n\n"
            "Do NOT use for: detailed node tree structure (use blender_get_node_tree with tree_type=SHADER)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "enum": ["all", "used_only", "unused_only"],
                    "default": "all",
                    "description": "Filter materials by usage status.",
                },
                "name_pattern": {
                    "type": "string",
                    "description": "Glob pattern to filter by name (e.g. '*Metal*').",
                },
            },
            "additionalProperties": False,
        },
        annotations={
            "title": "List Materials",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.get_materials",
    ),
    _tool(
        name="blender_get_scene",
        description=(
            "Get scene-level global information — statistics, render engine config, world "
            "environment basics, timeline/FPS, Blender version, memory usage.\n\n"
            "Use this when: you need the high-level project overview.\n\n"
            "Do NOT use for: object details (use blender_get_objects or blender_get_object_data)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "include": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["stats", "render", "world", "timeline", "version", "memory"],
                    },
                    "default": ["stats", "render", "timeline"],
                    "description": "Which sections to include in the response.",
                },
            },
            "additionalProperties": False,
        },
        annotations={
            "title": "Get Scene Info",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.get_scene",
    ),
    _tool(
        name="blender_get_collections",
        description=(
            "Return the collection hierarchy tree. Each collection shows name, child collections, "
            "object count, viewport/render visibility, and color tag.\n\n"
            "Use this when: you need to understand scene organization.\n\n"
            "Do NOT use for: listing objects (use blender_get_objects with collection filter)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "root": {
                    "type": "string",
                    "description": "Start from this collection. Default: Scene Collection (root).",
                },
                "depth": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 10,
                    "description": "Maximum recursion depth for the tree.",
                },
            },
            "additionalProperties": False,
        },
        annotations={
            "title": "Get Collection Tree",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.get_collections",
    ),
    _tool(
        name="blender_get_armature_data",
        description=(
            "Read armature/bone data — bone hierarchy, head/tail/roll positions, bone constraints, "
            "rest/pose transforms, bone groups, IK chains.\n\n"
            "Use this when: you need bone/rig information for animation or rigging.\n\n"
            "Do NOT use for: general object info (use blender_get_object_data)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "armature_name": {
                    "type": "string",
                    "description": "Name of the armature object.",
                },
                "include": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["hierarchy", "poses", "constraints", "bone_groups", "ik_chains"],
                    },
                    "default": ["hierarchy"],
                    "description": "Which data sections to include.",
                },
                "bone_filter": {
                    "type": "string",
                    "description": "Glob pattern to filter bones by name (e.g. 'Arm*' or '*_L').",
                },
            },
            "required": ["armature_name"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Get Armature/Bone Data",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.get_armature_data",
    ),
    _tool(
        name="blender_get_images",
        description=(
            "List all images/textures in the file — name, dimensions, format, file path, "
            "packed status, color space, user count.\n\n"
            "Use this when: you need to audit textures or find missing image files.\n\n"
            "Do NOT use for: viewport screenshot (use blender_capture_viewport)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "filter": {
                    "type": "string",
                    "enum": ["all", "packed", "external", "missing", "unused"],
                    "default": "all",
                    "description": "Filter images by status.",
                },
                "name_pattern": {
                    "type": "string",
                    "description": "Glob pattern to filter by name.",
                },
            },
            "additionalProperties": False,
        },
        annotations={
            "title": "List Images/Textures",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.get_images",
    ),
    _tool(
        name="blender_capture_viewport",
        description=(
            "Capture a screenshot of the current 3D viewport. This is the LLM's only way "
            "to 'see' the visual result. Supports different shading modes and camera view.\n\n"
            "Use this when: you need visual verification of changes.\n\n"
            "Do NOT use for: scene data queries (use blender_get_scene)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "shading": {
                    "type": "string",
                    "enum": ["SOLID", "MATERIAL", "RENDERED", "WIREFRAME"],
                    "default": "SOLID",
                    "description": "Viewport shading mode for the capture.",
                },
                "camera_view": {
                    "type": "boolean",
                    "default": False,
                    "description": "If true, capture from the active camera's perspective.",
                },
                "format": {
                    "type": "string",
                    "enum": ["PNG", "JPEG"],
                    "default": "PNG",
                    "description": "Image format for the capture.",
                },
            },
            "additionalProperties": False,
        },
        annotations={
            "title": "Capture Viewport Screenshot",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.capture_viewport",
    ),
    _tool(
        name="blender_get_selection",
        description=(
            "Return the current selection state — selected objects, active object, "
            "current interaction mode, and active tool.\n\n"
            "Use this when: you need to understand what the user is currently working on.\n\n"
            "Do NOT use for: listing all objects (use blender_get_objects)."
        ),
        input_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        annotations={
            "title": "Get Selection State",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.get_selection",
    ),
]

# ---------------------------------------------------------------------------
# Declarative Write Layer (3 Tools)
# ---------------------------------------------------------------------------

_DECLARATIVE_TOOLS = [
    _tool(
        name="blender_edit_nodes",
        description=(
            "Edit any node tree in Blender — add/remove nodes, connect/disconnect sockets, "
            "set node input values and properties. Supports all 6 node tree contexts. "
            "Operations are executed in order within a single call.\n\n"
            "Use this when: you need to build or modify shader, compositor, or geometry node graphs.\n\n"
            "Do NOT use for: high-level PBR properties (use blender_manage_material), "
            "reading node trees (use blender_get_node_tree first)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "tree_type": {
                    "type": "string",
                    "enum": ["SHADER", "COMPOSITOR", "GEOMETRY"],
                    "description": "Type of node tree to edit.",
                },
                "context": {
                    "type": "string",
                    "enum": ["OBJECT", "WORLD", "LINESTYLE", "SCENE", "MODIFIER", "TOOL"],
                    "description": (
                        "Context within the tree type. "
                        "SHADER: OBJECT|WORLD|LINESTYLE. "
                        "COMPOSITOR: SCENE. "
                        "GEOMETRY: MODIFIER|TOOL."
                    ),
                },
                "target": {
                    "type": "string",
                    "description": (
                        "Target name. For SHADER/OBJECT: material name. "
                        "For SHADER/WORLD: world name. "
                        "For GEOMETRY/MODIFIER: 'ObjectName/ModifierName'. "
                        "For COMPOSITOR/SCENE: omit or scene name."
                    ),
                },
                "operations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": [
                                    "add_node",
                                    "remove_node",
                                    "connect",
                                    "disconnect",
                                    "set_value",
                                    "set_property",
                                ],
                                "description": "The node operation to perform.",
                            },
                            "type": {
                                "type": "string",
                                "description": (
                                    "For add_node: Blender node type identifier (e.g. 'ShaderNodeBsdfPrincipled')."
                                ),
                            },
                            "name": {
                                "type": "string",
                                "description": (
                                    "Node name. For add_node: desired name. For remove_node: name to remove."
                                ),
                            },
                            "location": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 2,
                                "maxItems": 2,
                                "description": "For add_node: [x, y] position in the node editor.",
                            },
                            "node": {
                                "type": "string",
                                "description": "For set_value/set_property/disconnect: target node name.",
                            },
                            "input": {
                                "type": "string",
                                "description": "For set_value: input socket name (e.g. 'Base Color', 'Metallic').",
                            },
                            "value": {
                                "description": "For set_value: the value to set. Type depends on the socket.",
                            },
                            "property": {
                                "type": "string",
                                "description": (
                                    "For set_property: node property name (e.g. 'interpolation', 'blend_type')."
                                ),
                            },
                            "from_node": {"type": "string", "description": "For connect: source node name."},
                            "from_socket": {"type": "string", "description": "For connect: source output socket name."},
                            "to_node": {"type": "string", "description": "For connect: destination node name."},
                            "to_socket": {
                                "type": "string",
                                "description": "For connect: destination input socket name.",
                            },
                        },
                        "required": ["action"],
                    },
                    "description": "Array of node operations to execute in order.",
                },
            },
            "required": ["tree_type", "context", "operations"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Edit Node Tree",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.edit_nodes",
    ),
    _tool(
        name="blender_edit_animation",
        description=(
            "Edit animation data — insert/modify/delete keyframes, manage NLA strips, "
            "set drivers, control shape keys, and configure timeline settings.\n\n"
            "Use this when: you need to create or modify animation.\n\n"
            "Do NOT use for: reading animation data (use blender_get_animation_data)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "insert_keyframe",
                        "delete_keyframe",
                        "modify_keyframe",
                        "add_nla_strip",
                        "modify_nla_strip",
                        "remove_nla_strip",
                        "add_driver",
                        "remove_driver",
                        "set_shape_key",
                        "set_frame",
                        "set_frame_range",
                    ],
                    "description": "The animation operation to perform.",
                },
                "object_name": {"type": "string", "description": "Target object name."},
                "data_path": {
                    "type": "string",
                    "description": "Property path for keyframe/driver (e.g. 'location', 'rotation_euler', 'scale').",
                },
                "index": {
                    "type": "integer",
                    "default": -1,
                    "description": "Array index for the property (-1 for all channels, 0/1/2 for X/Y/Z).",
                },
                "frame": {"type": "integer", "description": "Frame number for keyframe operations."},
                "value": {"description": "Value for keyframe or shape key (number, array, or boolean)."},
                "interpolation": {
                    "type": "string",
                    "enum": [
                        "CONSTANT",
                        "LINEAR",
                        "BEZIER",
                        "SINE",
                        "QUAD",
                        "CUBIC",
                        "QUART",
                        "QUINT",
                        "EXPO",
                        "CIRC",
                        "BACK",
                        "BOUNCE",
                        "ELASTIC",
                    ],
                    "description": "Keyframe interpolation type.",
                },
                "nla_action": {"type": "string", "description": "Action name for NLA strip operations."},
                "nla_start_frame": {"type": "integer", "description": "Start frame for NLA strip."},
                "nla_strip_name": {"type": "string", "description": "NLA strip name for modify/remove."},
                "driver_expression": {"type": "string", "description": "Python expression for driver."},
                "shape_key_name": {"type": "string", "description": "Shape key name for set_shape_key."},
                "fps": {"type": "number", "description": "Frames per second (for set_frame_range)."},
                "frame_start": {"type": "integer", "description": "Start frame (for set_frame_range or set_frame)."},
                "frame_end": {"type": "integer", "description": "End frame (for set_frame_range)."},
            },
            "required": ["action"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Edit Animation",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.edit_animation",
    ),
    _tool(
        name="blender_edit_sequencer",
        description=(
            "Edit the Video Sequence Editor (VSE) — add/modify/delete strips, add transitions "
            "and effects. Supports video, image, audio, text, color, and adjustment layer strips.\n\n"
            "Use this when: you need to edit video sequences or add VSE effects.\n\n"
            "Do NOT use for: compositor node effects (use blender_edit_nodes with tree_type=COMPOSITOR)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add_strip", "modify_strip", "delete_strip", "add_effect", "add_transition", "move_strip"],
                    "description": "The sequencer operation to perform.",
                },
                "strip_type": {
                    "type": "string",
                    "enum": ["VIDEO", "IMAGE", "AUDIO", "TEXT", "COLOR", "ADJUSTMENT"],
                    "description": "Type of strip to add (for add_strip action).",
                },
                "filepath": {
                    "type": "string",
                    "description": "File path for VIDEO/IMAGE/AUDIO strips.",
                    "maxLength": 4096,
                },
                "channel": {"type": "integer", "minimum": 1, "description": "VSE channel number."},
                "frame_start": {"type": "integer", "description": "Start frame of the strip."},
                "frame_end": {"type": "integer", "description": "End frame of the strip."},
                "strip_name": {"type": "string", "description": "Strip name for modify/delete/move operations."},
                "text": {"type": "string", "description": "Text content for TEXT strips."},
                "font_size": {"type": "number", "description": "Font size for TEXT strips."},
                "color": _color3_4("Color [r,g,b] or [r,g,b,a] for TEXT/COLOR strips."),
                "effect_type": {
                    "type": "string",
                    "enum": [
                        "TRANSFORM",
                        "SPEED",
                        "GLOW",
                        "GAUSSIAN_BLUR",
                        "COLOR_BALANCE",
                        "ALPHA_OVER",
                        "ALPHA_UNDER",
                        "MULTIPLY",
                    ],
                    "description": "Effect type for add_effect action.",
                },
                "transition_type": {
                    "type": "string",
                    "enum": ["CROSS", "WIPE", "GAMMA_CROSS"],
                    "description": "Transition type for add_transition action.",
                },
                "transition_duration": {"type": "integer", "description": "Duration in frames for transitions."},
                "settings": {"type": "object", "description": "Additional strip/effect-specific settings."},
            },
            "required": ["action"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Edit Video Sequencer",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.edit_sequencer",
    ),
]

# ---------------------------------------------------------------------------
# Imperative Write Layer (10 Tools)
# ---------------------------------------------------------------------------

_IMPERATIVE_TOOLS = [
    _tool(
        name="blender_create_object",
        description=(
            "Create a new object in the Blender scene. Supports mesh primitives, lights, cameras, "
            "curves, empties, armatures, and text objects. Automatically linked to the specified collection.\n\n"
            "Use this when: you need to add a new object to the scene.\n\n"
            "Do NOT use for: modifying existing objects (use blender_modify_object), "
            "adding modifiers (use blender_manage_modifier), assigning materials (use blender_manage_material)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name for the new object.", "maxLength": 63},
                "object_type": {
                    "type": "string",
                    "enum": ["MESH", "LIGHT", "CAMERA", "CURVE", "EMPTY", "ARMATURE", "TEXT"],
                    "default": "MESH",
                    "description": "Type of object to create.",
                },
                "primitive": {
                    "type": "string",
                    "enum": ["cube", "sphere", "cylinder", "cone", "plane", "torus", "icosphere"],
                    "description": "Mesh primitive shape. Only for object_type=MESH.",
                },
                "size": {
                    "type": "number",
                    "default": 2.0,
                    "minimum": 0.001,
                    "description": "Size of mesh primitive in Blender units.",
                },
                "segments": {
                    "type": "integer",
                    "default": 32,
                    "minimum": 3,
                    "description": "Segments for sphere/cylinder/cone/torus.",
                },
                "light_type": {
                    "type": "string",
                    "enum": ["POINT", "SUN", "SPOT", "AREA"],
                    "default": "POINT",
                    "description": "Light type. Only for object_type=LIGHT.",
                },
                "energy": {"type": "number", "default": 1000, "description": "Light energy in watts. Only for LIGHT."},
                "color": _vec3("Light color [r,g,b] range 0-1. Only for LIGHT."),
                "lens": {"type": "number", "default": 50, "description": "Camera focal length in mm. Only for CAMERA."},
                "clip_start": {"type": "number", "default": 0.1, "description": "Camera near clip. Only for CAMERA."},
                "clip_end": {"type": "number", "default": 1000, "description": "Camera far clip. Only for CAMERA."},
                "set_active_camera": {
                    "type": "boolean",
                    "default": False,
                    "description": "Set as active scene camera. Only for CAMERA.",
                },
                "curve_type": {
                    "type": "string",
                    "enum": ["BEZIER", "NURBS", "POLY"],
                    "default": "BEZIER",
                    "description": "Spline type. Only for CURVE.",
                },
                "body": {"type": "string", "description": "Text content. Only for TEXT."},
                "extrude": {"type": "number", "default": 0, "description": "Extrude depth for TEXT."},
                "location": _vec3("3D position [x, y, z].", default=[0, 0, 0]),
                "rotation": _vec3("Euler rotation [x, y, z] in radians.", default=[0, 0, 0]),
                "scale": _vec3("Scale [x, y, z].", default=[1, 1, 1]),
                "collection": {
                    "type": "string",
                    "description": "Collection to link to. Uses scene collection if omitted.",
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Create Object",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.create_object",
    ),
    _tool(
        name="blender_modify_object",
        description=(
            "Modify an existing object — transform, parent, visibility, rename, set origin, or delete. "
            "The 'delete' action is destructive and irreversible.\n\n"
            "Use this when: you need to change an object's properties.\n\n"
            "Do NOT use for: modifiers (use blender_manage_modifier), materials (use blender_manage_material), "
            "constraints (use blender_manage_constraints), physics (use blender_manage_physics)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the object to modify."},
                "location": _vec3("New 3D position [x, y, z]."),
                "rotation": _vec3("New Euler rotation [x, y, z] in radians."),
                "scale": _vec3("New scale [x, y, z]."),
                "parent": {"type": "string", "description": "Parent object name. Set to '' to clear parent."},
                "visible": {"type": "boolean", "description": "Viewport visibility."},
                "hide_render": {"type": "boolean", "description": "Hide from render."},
                "new_name": {"type": "string", "description": "Rename the object.", "maxLength": 63},
                "active": {"type": "boolean", "description": "Set as active object."},
                "selected": {"type": "boolean", "description": "Set selection state."},
                "origin": {
                    "type": "string",
                    "enum": ["GEOMETRY", "CURSOR", "MEDIAN"],
                    "description": "Set origin point.",
                },
                "delete": {
                    "type": "boolean",
                    "default": False,
                    "description": "If true, delete this object. DESTRUCTIVE.",
                },
                "delete_data": {
                    "type": "boolean",
                    "default": True,
                    "description": "When deleting, also delete underlying data block.",
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Modify Object",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.modify_object",
    ),
    _tool(
        name="blender_manage_material",
        description=(
            "Create, edit, assign, duplicate, or delete materials. For high-level PBR property editing only. "
            "The 'delete' action is destructive and irreversible.\n\n"
            "Use this when: you need to create/configure materials or assign them to objects.\n\n"
            "Do NOT use for: node-level shader editing (use blender_edit_nodes with tree_type=SHADER)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "edit", "assign", "unassign", "duplicate", "delete"],
                    "description": "The material operation.",
                },
                "name": {"type": "string", "description": "Material name."},
                "base_color": _rgba4("Base color [r,g,b,a] range 0-1."),
                "metallic": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Metallic value 0-1. 0=dielectric, 1=full metal.",
                },
                "roughness": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Roughness value 0-1. 0=mirror, 1=diffuse.",
                },
                "specular": {"type": "number", "minimum": 0, "maximum": 1, "description": "Specular value 0-1."},
                "alpha": {"type": "number", "minimum": 0, "maximum": 1, "description": "Alpha value 0-1."},
                "emission_color": _rgba4("Emission color [r,g,b,a]."),
                "emission_strength": {"type": "number", "description": "Emission strength."},
                "use_fake_user": {"type": "boolean", "description": "Prevent auto-deletion when unused."},
                "object_name": {"type": "string", "description": "Object name for assign/unassign."},
                "slot": {"type": "integer", "minimum": 0, "description": "Material slot index (0-based)."},
            },
            "required": ["action", "name"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Manage Material",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.manage_material",
    ),
    _tool(
        name="blender_manage_modifier",
        description=(
            "Add, configure, apply, remove, or reorder modifiers on an object. "
            "The 'apply' and 'remove' actions are destructive.\n\n"
            "Use this when: you need to work with modifiers.\n\n"
            "Do NOT use for: reading modifier details (use blender_get_object_data with include=['modifiers'])."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "configure", "apply", "remove", "move_up", "move_down"],
                    "description": "The modifier operation.",
                },
                "object_name": {"type": "string", "description": "Name of the object."},
                "modifier_name": {"type": "string", "description": "Modifier name."},
                "modifier_type": {
                    "type": "string",
                    "enum": [
                        "SUBSURF",
                        "MIRROR",
                        "ARRAY",
                        "BOOLEAN",
                        "SOLIDIFY",
                        "BEVEL",
                        "SHRINKWRAP",
                        "DECIMATE",
                        "REMESH",
                        "WEIGHTED_NORMAL",
                        "SIMPLE_DEFORM",
                        "SKIN",
                        "WIREFRAME",
                        "SCREW",
                        "DISPLACE",
                        "CAST",
                        "SMOOTH",
                        "LAPLACIANSMOOTH",
                        "CORRECTIVE_SMOOTH",
                        "CURVE",
                        "LATTICE",
                        "WARP",
                        "WAVE",
                        "CLOTH",
                        "COLLISION",
                        "ARMATURE",
                        "MESH_DEFORM",
                        "HOOK",
                        "SURFACE_DEFORM",
                        "DATA_TRANSFER",
                        "NORMAL_EDIT",
                        "UV_PROJECT",
                        "UV_WARP",
                        "VERTEX_WEIGHT_EDIT",
                        "VERTEX_WEIGHT_MIX",
                        "VERTEX_WEIGHT_PROXIMITY",
                        "NODES",
                    ],
                    "description": "Modifier type. For add action only.",
                },
                "settings": {
                    "type": "object",
                    "description": 'Modifier settings as key-value pairs (e.g. {"levels": 3} for SUBSURF).',
                },
            },
            "required": ["action", "object_name"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Manage Modifier",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.manage_modifier",
    ),
    _tool(
        name="blender_manage_collection",
        description=(
            "Create, delete, or manage collections — link/unlink objects, set parent, control visibility.\n\n"
            "Use this when: you need to organize scene objects into collections.\n\n"
            "Do NOT use for: reading collection data (use blender_get_collections)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "delete", "link_object", "unlink_object", "set_visibility", "set_parent"],
                    "description": "The collection operation.",
                },
                "collection_name": {"type": "string", "description": "Name of the collection."},
                "object_name": {"type": "string", "description": "Object name for link/unlink."},
                "parent": {"type": "string", "description": "Parent collection name."},
                "hide_viewport": {"type": "boolean", "description": "Hide in viewport (for set_visibility)."},
                "hide_render": {"type": "boolean", "description": "Hide in render (for set_visibility)."},
                "color_tag": {
                    "type": "string",
                    "enum": [
                        "NONE",
                        "COLOR_01",
                        "COLOR_02",
                        "COLOR_03",
                        "COLOR_04",
                        "COLOR_05",
                        "COLOR_06",
                        "COLOR_07",
                        "COLOR_08",
                    ],
                    "description": "Color tag for visual organization.",
                },
            },
            "required": ["action", "collection_name"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Manage Collection",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.manage_collection",
    ),
    _tool(
        name="blender_manage_uv",
        description=(
            "UV mapping operations — mark/clear seams, unwrap with various algorithms, "
            "pack/scale UV islands, manage UV layers.\n\n"
            "Use this when: you need algorithmic UV unwrapping or UV layer management.\n\n"
            "Do NOT use for: UV painting (use blender_execute_operator)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "mark_seam",
                        "clear_seam",
                        "unwrap",
                        "smart_project",
                        "cube_project",
                        "cylinder_project",
                        "sphere_project",
                        "lightmap_pack",
                        "pack_islands",
                        "average_island_scale",
                        "add_uv_map",
                        "remove_uv_map",
                        "set_active_uv",
                    ],
                    "description": "The UV operation.",
                },
                "object_name": {"type": "string", "description": "Name of the mesh object."},
                "uv_map_name": {"type": "string", "description": "UV map name for add/remove/set_active."},
                "angle_limit": {
                    "type": "number",
                    "default": 66.0,
                    "minimum": 0,
                    "maximum": 89,
                    "description": "Angle limit in degrees for smart_project.",
                },
                "island_margin": {
                    "type": "number",
                    "default": 0.02,
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Margin between UV islands.",
                },
                "correct_aspect": {
                    "type": "boolean",
                    "default": True,
                    "description": "Correct for non-square textures.",
                },
                "selection_mode": {
                    "type": "string",
                    "enum": ["SHARP_EDGES", "ANGLE_BASED", "ALL_EDGES"],
                    "description": "Auto-select edges for mark_seam.",
                },
            },
            "required": ["action", "object_name"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Manage UV Mapping",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.manage_uv",
    ),
    _tool(
        name="blender_manage_constraints",
        description=(
            "Add, configure, remove, enable/disable, or reorder constraints on objects or bones.\n\n"
            "Use this when: you need to set up rigging constraints or motion control.\n\n"
            "Do NOT use for: reading constraints (use blender_get_object_data with include=['constraints'] "
            "or blender_get_armature_data with include=['constraints'])."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "configure", "remove", "enable", "disable", "move_up", "move_down"],
                    "description": "The constraint operation.",
                },
                "target_type": {
                    "type": "string",
                    "enum": ["OBJECT", "BONE"],
                    "default": "OBJECT",
                    "description": "Whether constraint is on an object or a bone.",
                },
                "target_name": {"type": "string", "description": "Object name, or 'ArmatureName/BoneName' for BONE."},
                "constraint_name": {"type": "string", "description": "Constraint name."},
                "constraint_type": {
                    "type": "string",
                    "enum": [
                        "COPY_LOCATION",
                        "COPY_ROTATION",
                        "COPY_SCALE",
                        "COPY_TRANSFORMS",
                        "LIMIT_DISTANCE",
                        "LIMIT_LOCATION",
                        "LIMIT_ROTATION",
                        "LIMIT_SCALE",
                        "TRACK_TO",
                        "DAMPED_TRACK",
                        "LOCKED_TRACK",
                        "IK",
                        "STRETCH_TO",
                        "FLOOR",
                        "CHILD_OF",
                        "FOLLOW_PATH",
                        "CLAMP_TO",
                        "PIVOT",
                        "MAINTAIN_VOLUME",
                        "TRANSFORMATION",
                        "SHRINKWRAP",
                        "ACTION",
                    ],
                    "description": "Constraint type for add action.",
                },
                "settings": {"type": "object", "description": "Constraint settings as key-value pairs."},
            },
            "required": ["action", "target_name"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Manage Constraints",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.manage_constraints",
    ),
    _tool(
        name="blender_manage_physics",
        description=(
            "Add, configure, remove, or bake physics simulations — rigid body, cloth, "
            "soft body, fluid, particle systems, and force fields.\n\n"
            "Use this when: you need physics simulations on objects.\n\n"
            "Do NOT use for: reading physics data (use blender_get_object_data with include=['physics'])."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "configure", "remove", "bake", "free_bake"],
                    "description": "The physics operation.",
                },
                "object_name": {"type": "string", "description": "Name of the object."},
                "physics_type": {
                    "type": "string",
                    "enum": [
                        "RIGID_BODY",
                        "RIGID_BODY_PASSIVE",
                        "CLOTH",
                        "SOFT_BODY",
                        "FLUID_DOMAIN",
                        "FLUID_FLOW",
                        "PARTICLE",
                        "FORCE_FIELD",
                    ],
                    "description": "Physics type for add action.",
                },
                "force_field_type": {
                    "type": "string",
                    "enum": ["WIND", "TURBULENCE", "VORTEX", "MAGNETIC", "HARMONIC", "CHARGE", "DRAG", "FORCE"],
                    "description": "Force field type. Only for physics_type=FORCE_FIELD.",
                },
                "settings": {"type": "object", "description": "Physics settings as key-value pairs."},
                "frame_start": {"type": "integer", "description": "Bake start frame."},
                "frame_end": {"type": "integer", "description": "Bake end frame."},
            },
            "required": ["action", "object_name"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Manage Physics",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.manage_physics",
    ),
    _tool(
        name="blender_setup_scene",
        description=(
            "Configure scene-level settings — render engine and quality, output resolution, "
            "world environment basics, and timeline/FPS.\n\n"
            "Use this when: you need to configure render, output, or timeline settings.\n\n"
            "Do NOT use for: detailed world shader editing "
            "(use blender_edit_nodes with tree_type=SHADER, context=WORLD)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "engine": {
                    "type": "string",
                    "enum": ["BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES"],
                    "description": "Render engine.",
                },
                "samples": {"type": "integer", "minimum": 1, "description": "Render samples."},
                "resolution_x": {"type": "integer", "minimum": 1, "description": "Output width in pixels."},
                "resolution_y": {"type": "integer", "minimum": 1, "description": "Output height in pixels."},
                "output_format": {
                    "type": "string",
                    "enum": ["PNG", "JPEG", "OPEN_EXR", "TIFF", "BMP", "FFMPEG"],
                    "description": "Output file format.",
                },
                "output_path": {"type": "string", "description": "Output file/directory path."},
                "film_transparent": {"type": "boolean", "description": "Render with transparent background."},
                "denoising": {"type": "boolean", "description": "Enable render denoising."},
                "denoiser": {"type": "string", "enum": ["OPTIX", "OPENIMAGEDENOISE"], "description": "Denoiser type."},
                "background_color": _rgba4("World background color [r,g,b,a]."),
                "background_strength": {"type": "number", "description": "World background strength."},
                "fps": {"type": "number", "description": "Frames per second."},
                "frame_start": {"type": "integer", "description": "Scene start frame."},
                "frame_end": {"type": "integer", "description": "Scene end frame."},
                "frame_current": {"type": "integer", "description": "Set current frame."},
            },
            "additionalProperties": False,
        },
        annotations={
            "title": "Setup Scene",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        internal_capability="blender.setup_scene",
    ),
    _tool(
        name="blender_edit_mesh",
        description=(
            "Edit mesh geometry with operations like extrude, inset, bevel, loop cut, dissolve, merge, "
            "subdivide, and delete.\n\n"
            "Use this when: you need to modify mesh topology.\n\n"
            "Do NOT use for: UV operations (use blender_manage_uv), object transforms (use blender_modify_object)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "object_name": {"type": "string", "description": "Name of the mesh object."},
                "action": {
                    "type": "string",
                    "enum": [
                        "extrude",
                        "extrude_individual",
                        "inset",
                        "bevel",
                        "loop_cut",
                        "dissolve_vertices",
                        "dissolve_edges",
                        "dissolve_faces",
                        "merge_vertices",
                        "subdivide",
                        "delete",
                        "select_all",
                        "select_mode",
                    ],
                    "description": "Mesh operation to perform.",
                },
                "selection": {
                    "type": "string",
                    "enum": ["VERT", "EDGE", "FACE", "ONLY_FACE", "ALL"],
                    "description": "Selection type for delete action.",
                },
                "select_action": {
                    "type": "string",
                    "enum": ["SELECT", "DESELECT", "TOGGLE", "INVERT"],
                    "description": "Action for select_all.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["VERT", "EDGE", "FACE"],
                    "description": "Selection mode for select_mode action.",
                },
                "threshold": {"type": "number", "description": "Merge threshold for merge_vertices.", "minimum": 0},
                "segments": {"type": "integer", "description": "Segments for bevel.", "minimum": 1},
                "number_cuts": {"type": "integer", "description": "Cuts for subdivide/loop_cut.", "minimum": 1},
                "amount": {"type": "number", "description": "Amount for inset/bevel."},
                "use_boundary": {"type": "boolean", "description": "For inset, inset boundary edges."},
                "use_even_offset": {"type": "boolean", "description": "For inset, use even offset."},
                "use_relative_offset": {"type": "boolean", "description": "For inset, use relative offset."},
                "use_verts": {"type": "boolean", "description": "For dissolve, also dissolve vertices."},
                "use_face_split": {"type": "boolean", "description": "For dissolve_edges, use face split."},
            },
            "required": ["object_name", "action"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Edit Mesh",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.edit_mesh",
    ),
]

# ---------------------------------------------------------------------------
# Fallback Layer (5 Tools)
# ---------------------------------------------------------------------------

_FALLBACK_TOOLS = [
    _tool(
        name="blender_execute_operator",
        description=(
            "Execute any Blender operator (bpy.ops.*) by name with parameters.\n\n"
            "Use this when: you need a Blender operation not covered by other tools. "
            "Prefer specialized tools first for better validation and error messages.\n\n"
            "Do NOT use for: object creation (use blender_create_object), "
            "script execution (use blender_execute_script), or import/export (use blender_import_export)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "operator": {
                    "type": "string",
                    "description": "Operator ID in 'category.name' format (e.g., 'mesh.primitive_cube_add').",
                },
                "params": {"type": "object", "description": "Operator parameters."},
                "context": {"type": "object", "description": "Context override (e.g., active_object, mode)."},
            },
            "required": ["operator"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Execute Blender Operator",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.execute_operator",
    ),
    _tool(
        name="blender_execute_script",
        description=(
            "Execute arbitrary Python code in Blender's Python environment. "
            "CAUTION: This tool has full access to Blender's API and filesystem.\n\n"
            "Use only when: no other tool can accomplish the task. "
            "Try blender_execute_operator first for standard Blender operations."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute. Has access to bpy, mathutils, and all Blender modules.",
                    "maxLength": 65536,
                },
            },
            "required": ["code"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Execute Python Script",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.execute_script",
    ),
    _tool(
        name="blender_import_export",
        description=(
            "Import or export asset files in various formats — FBX, OBJ, glTF, USD, Alembic, STL, and more.\n\n"
            "Use this when: you need to import assets into or export assets from Blender.\n\n"
            "Do NOT use for: scene manipulation (use blender_create_object or blender_modify_object)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["import", "export"],
                    "description": "Whether to import or export.",
                },
                "format": {
                    "type": "string",
                    "enum": [
                        "FBX",
                        "OBJ",
                        "GLTF",
                        "GLB",
                        "USD",
                        "USDC",
                        "USDA",
                        "ALEMBIC",
                        "STL",
                        "PLY",
                        "SVG",
                        "DAE",
                        "X3D",
                    ],
                    "description": "File format.",
                },
                "filepath": {
                    "type": "string",
                    "description": "Absolute file path for import source or export destination.",
                    "maxLength": 4096,
                },
                "settings": {"type": "object", "description": "Format-specific settings."},
            },
            "required": ["action", "format", "filepath"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Import/Export Assets",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
        internal_capability="blender.import_export",
    ),
    _tool(
        name="blender_render_scene",
        description=(
            "Render the current scene to an image file. Supports both still images and animations.\n\n"
            "Use this when: you need to render the scene to disk.\n\n"
            "Do NOT use for: viewport screenshots (use blender_capture_viewport), "
            "scene setup (use blender_setup_scene)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "output_path": {
                    "type": "string",
                    "description": "Absolute file path to save the rendered image.",
                    "maxLength": 4096,
                },
                "resolution_x": {
                    "type": "integer",
                    "description": "X resolution override.",
                    "minimum": 1,
                },
                "resolution_y": {
                    "type": "integer",
                    "description": "Y resolution override.",
                    "minimum": 1,
                },
                "samples": {
                    "type": "integer",
                    "description": "Render samples (Cycles only).",
                    "minimum": 1,
                },
                "animation": {
                    "type": "boolean",
                    "description": "If True, render animation frames.",
                },
                "frame_start": {
                    "type": "integer",
                    "description": "Start frame for animation render.",
                },
                "frame_end": {
                    "type": "integer",
                    "description": "End frame for animation render.",
                },
                "use_viewport": {
                    "type": "boolean",
                    "description": "If True, use viewport render (EEVEE only).",
                },
            },
            "required": ["output_path"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Render Scene",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
        internal_capability="blender.render_scene",
    ),
    _tool(
        name="blender_batch_execute",
        description=(
            "Execute multiple operations in a single batch request. "
            "Reduces MCP round-trips for complex workflows.\n\n"
            "Use this when: you need to perform multiple independent operations efficiently.\n\n"
            "Do NOT use for: single operations (use the specific tool directly)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "operations": {
                    "type": "array",
                    "description": "List of operations to execute.",
                    "minItems": 1,
                    "maxItems": 50,
                    "items": {
                        "type": "object",
                        "properties": {
                            "tool": {
                                "type": "string",
                                "description": "Tool name (e.g., 'blender_create_object').",
                            },
                            "params": {"type": "object", "description": "Tool parameters."},
                        },
                        "required": ["tool", "params"],
                        "additionalProperties": False,
                    },
                },
                "stop_on_error": {
                    "type": "boolean",
                    "description": "Stop on first error (default: true).",
                },
                "continue_on_error": {
                    "type": "boolean",
                    "description": "Continue even on errors (default: false).",
                },
            },
            "required": ["operations"],
            "additionalProperties": False,
        },
        annotations={
            "title": "Batch Execute",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        internal_capability="blender.batch_execute",
    ),
]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS: list[dict[str, Any]] = _PERCEPTION_TOOLS + _DECLARATIVE_TOOLS + _IMPERATIVE_TOOLS + _FALLBACK_TOOLS

_TOOL_INDEX: dict[str, dict[str, Any]] = {t["name"]: t for t in TOOL_DEFINITIONS}


def get_tool(name: str) -> dict[str, Any] | None:
    """Get a tool definition by name."""
    return _TOOL_INDEX.get(name)


def list_tools() -> list[dict[str, Any]]:
    """Return all tool definitions."""
    return TOOL_DEFINITIONS
