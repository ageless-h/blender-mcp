# -*- coding: utf-8 -*-
"""Node tree editor — add/remove nodes, connect/disconnect, set values."""

from __future__ import annotations

import logging
import re
from typing import Any

from ..error_codes import ErrorCode
from ..response import _error, _ok, bpy_unavailable_error, check_bpy_available
from ..utils.property_parser import coerce_value
from .reader import _resolve_node_tree

logger = logging.getLogger(__name__)


_NODE_TYPE_CACHE: list[dict[str, str]] | None = None


def _discover_node_types() -> list[dict[str, str]]:
    """Dynamically discover all registered node types from bpy.types.

    Returns a list of {bl_idname, name, category} dicts.  Falls back to
    _ENGLISH_NODE_NAMES if bpy is unavailable.
    """
    global _NODE_TYPE_CACHE
    if _NODE_TYPE_CACHE is not None:
        return _NODE_TYPE_CACHE

    try:
        import bpy  # type: ignore

        result: list[dict[str, str]] = []
        seen: set[str] = set()
        for typename in dir(bpy.types):
            cls = getattr(bpy.types, typename)
            if not isinstance(cls, type):
                continue
            if not issubclass(cls, getattr(bpy.types, "Node", type(None))):
                continue
            if cls is bpy.types.Node:
                continue
            bl_id = getattr(cls, "bl_idname", None)
            if bl_id and bl_id not in seen:
                seen.add(bl_id)
                name = getattr(cls, "bl_label", bl_id)
                category = getattr(cls, "bl_icon", "")
                result.append({"bl_idname": bl_id, "name": name, "category": category})

        if result:
            _NODE_TYPE_CACHE = result
            return result
    except (ImportError, AttributeError):
        pass

    fallback = [{"bl_idname": v, "name": k, "category": "static"} for k, v in _ENGLISH_NODE_NAMES.items()]
    _NODE_TYPE_CACHE = fallback
    return fallback


# English display names that LLMs commonly use → bl_idname identifiers.
# In localized Blender, default nodes get renamed (e.g. "Principled BSDF"
# becomes "原理化 BSDF" in Chinese), but bl_idname is always stable.
_ENGLISH_NODE_NAMES: dict[str, str] = {
    # --- Shader ---
    "Principled BSDF": "ShaderNodeBsdfPrincipled",
    "Material Output": "ShaderNodeOutputMaterial",
    "Diffuse BSDF": "ShaderNodeBsdfDiffuse",
    "Glossy BSDF": "ShaderNodeBsdfGlossy",
    "Glass BSDF": "ShaderNodeBsdfGlass",
    "Emission": "ShaderNodeEmission",
    "Mix Shader": "ShaderNodeMixShader",
    "Add Shader": "ShaderNodeAddShader",
    "Transparent BSDF": "ShaderNodeBsdfTransparent",
    "Refraction BSDF": "ShaderNodeBsdfRefraction",
    "Subsurface Scattering": "ShaderNodeSubsurfaceScattering",
    "Holdout": "ShaderNodeHoldout",
    "Ambient Occlusion": "ShaderNodeAmbientOcclusion",
    "Volume Scatter": "ShaderNodeVolumeScatter",
    "Volume Absorption": "ShaderNodeVolumeAbsorption",
    "Principled Volume": "ShaderNodeVolumePrincipled",
    # --- Shader Inputs ---
    "Texture Coordinate": "ShaderNodeTexCoord",
    "Mapping": "ShaderNodeMapping",
    "Attribute": "ShaderNodeAttribute",
    "Fresnel": "ShaderNodeFresnel",
    "Layer Weight": "ShaderNodeLayerWeight",
    "Light Path": "ShaderNodeLightPath",
    "Object Info": "ShaderNodeObjectInfo",
    "Particle Info": "ShaderNodeParticleInfo",
    "Camera Data": "ShaderNodeCameraData",
    "New Geometry": "ShaderNodeNewGeometry",
    "Wireframe": "ShaderNodeWireframe",
    "UV Map": "ShaderNodeUVMap",
    "Value": "ShaderNodeValue",
    "RGB": "ShaderNodeRGB",
    "Color Ramp": "ShaderNodeValToRGB",
    "Curve Time": "ShaderNodeCurveTime",
    # --- Shader Textures ---
    "Image Texture": "ShaderNodeTexImage",
    "Environment Texture": "ShaderNodeTexEnvironment",
    "Noise Texture": "ShaderNodeTexNoise",
    "Musgrave Texture": "ShaderNodeTexMusgrave",
    "Voronoi Texture": "ShaderNodeTexVoronoi",
    "Brick Texture": "ShaderNodeTexBrick",
    "Checker Texture": "ShaderNodeTexChecker",
    "Gradient Texture": "ShaderNodeTexGradient",
    "Magic Texture": "ShaderNodeTexMagic",
    "Wave Texture": "ShaderNodeTexWave",
    "Color Attribute": "ShaderNodeColorAttribute",
    # --- Shader Vector ---
    "Bump": "ShaderNodeBump",
    "Normal Map": "ShaderNodeNormalMap",
    "Normal": "ShaderNodeNormal",
    "Vector Math": "ShaderNodeVectorMath",
    "Vector Rotate": "ShaderNodeVectorRotate",
    "Curves": "ShaderNodeVectorCurve",
    "Displacement": "ShaderNodeDisplacement",
    "Mix": "ShaderNodeMix",
    "Math": "ShaderNodeMath",
    "Separate Color": "ShaderNodeSeparateColor",
    "Combine Color": "ShaderNodeCombineColor",
    "Separate XYZ": "ShaderNodeSeparateXYZ",
    "Combine XYZ": "ShaderNodeCombineXYZ",
    "Hue/Saturation": "ShaderNodeHueSaturation",
    "Bright/Contrast": "ShaderNodeBrightContrast",
    "Gamma": "ShaderNodeGamma",
    "Invert Color": "ShaderNodeInvert",
    "Color Balance": "ShaderNodeColorBalance",
    # --- Compositor ---
    "Composite": "CompositorNodeComposite",
    "Render Layers": "CompositorNodeRLayers",
    "Viewer": "CompositorNodeViewer",
    "Split Viewer": "CompositorNodeSplitViewer",
    "File Output": "CompositorNodeOutputFile",
    "Glare": "CompositorNodeGlare",
    "Blur": "CompositorNodeBlur",
    "Denoise": "CompositorNodeDenoise",
    "Alpha Over": "CompositorNodeAlphaOver",
    "Hue Correct": "CompositorNodeHueCorrect",
    "Curve RGB": "CompositorNodeCurveRGB",
    "Levels": "CompositorNodeLevels",
    "Color Correction": "CompositorNodeColorCorrection",
    "Lens Distortion": "CompositorNodeLensdist",
    "Map UV": "CompositorNodeMapUV",
    "Defocus": "CompositorNodeDefocus",
    "Double Edge Mask": "CompositorNodeDoubleEdgeMask",
    "Cryptomatte": "CompositorNodeCryptomatte",
    "Keying": "CompositorNodeKeying",
    # --- Geometry Nodes ---
    "Group Input": "NodeGroupInput",
    "Group Output": "NodeGroupOutput",
    "Transform Geometry": "GeometryNodeTransform",
    "Set Position": "GeometryNodeSetPosition",
    "Subdivision Surface": "GeometryNodeSubdivisionSurface",
    "Mesh to Points": "GeometryNodeMeshToPoints",
    "Instance on Points": "GeometryNodeInstanceOnPoints",
    "Realize Instances": "GeometryNodeRealizeInstances",
    "Join Geometry": "GeometryNodeJoinGeometry",
    "Separate Geometry": "GeometryNodeSeparateGeometry",
    "Delete Geometry": "GeometryNodeDeleteGeometry",
    "Extrude Mesh": "GeometryNodeExtrudeMesh",
    "Scale Elements": "GeometryNodeScaleElements",
    "Mesh Boolean": "GeometryNodeMeshBoolean",
    "Sample Nearest Surface": "GeometryNodeSampleNearestSurface",
    "Sample Index": "GeometryNodeSampleIndex",
    "Field at Index": "GeometryNodeFieldAtIndex",
    "Random Value": "GeometryNodeInputRandom",
    "Position": "GeometryNodeInputPosition",
    "Index": "GeometryNodeInputIndex",
    "ID": "GeometryNodeInputID",
    "Collection Info": "GeometryNodeCollectionInfo",
    "Material Selection": "GeometryNodeMaterialSelection",
    "Set Material": "GeometryNodeSetMaterial",
    "Set Material Index": "GeometryNodeSetMaterialIndex",
    "Proximity": "GeometryNodeProximity",
    "Raycast": "GeometryNodeRaycast",
    "Distribute Points on Faces": "GeometryNodeDistributePointsOnFaces",
    "Merge by Distance": "GeometryNodeMergeByDistance",
    "Mesh to Curve": "GeometryNodeMeshToCurve",
    "Curve to Mesh": "GeometryNodeCurveToMesh",
    "Trim Curve": "GeometryNodeTrimCurve",
    "Curve Length": "GeometryNodeCurveLength",
    "Resample Curve": "GeometryNodeResampleCurve",
    "Named Attribute": "GeometryNodeInputNamedAttribute",
    "Store Named Attribute": "GeometryNodeStoreNamedAttribute",
    "Switch": "GeometryNodeSwitch",
    "BoundingBox": "GeometryNodeBoundBox",
}

# Pre-computed lookup sets for O(1) resolution
_IDNAME_SET: set[str] = set(_ENGLISH_NODE_NAMES.values())
_NAME_TO_IDNAME: dict[str, str] = {name.lower(): idname for name, idname in _ENGLISH_NODE_NAMES.items()}


# Commonly-mistyped bl_idnames that differ from the actual Blender identifier.
_WRONG_BL_IDNAMES: dict[str, str] = {
    "ShaderNodeNoiseTexture": "ShaderNodeTexNoise",
    "ShaderNodeMusgraveTexture": "ShaderNodeTexMusgrave",
    "ShaderNodeVoronoiTexture": "ShaderNodeTexVoronoi",
    "ShaderNodeBrickTexture": "ShaderNodeTexBrick",
    "ShaderNodeCheckerTexture": "ShaderNodeTexChecker",
    "ShaderNodeGradientTexture": "ShaderNodeTexGradient",
    "ShaderNodeMagicTexture": "ShaderNodeTexMagic",
    "ShaderNodeWaveTexture": "ShaderNodeTexWave",
    "ShaderNodeEnvironmentTexture": "ShaderNodeTexEnvironment",
    "ShaderNodeImageTexture": "ShaderNodeTexImage",
    "ShaderNodeColorAttribute": "ShaderNodeColorAttribute",
}


def _resolve_node_type(type_str: str) -> str:
    """Resolve a node type string to a valid bl_idname.

    Tries in order:
    1. Pass through as-is (works for exact bl_idname like ShaderNodeTexNoise)
    2. Look up in _ENGLISH_NODE_NAMES keys (friendly name -> bl_idname)
    3. Correct commonly-mistyped bl_idnames via _WRONG_BL_IDNAMES
    4. Search dynamically discovered node types by name
    """
    if not type_str:
        return type_str
    if type_str in _IDNAME_SET:
        return type_str
    if type_str in _NAME_TO_IDNAME:
        return _NAME_TO_IDNAME[type_str]
    idname = _ENGLISH_NODE_NAMES.get(type_str)
    if idname:
        return idname
    if type_str in _WRONG_BL_IDNAMES:
        return _WRONG_BL_IDNAMES[type_str]
    lower_type = type_str.lower()
    if lower_type in _NAME_TO_IDNAME:
        return _NAME_TO_IDNAME[lower_type]
    for entry in _discover_node_types():
        if entry["name"].lower() == lower_type:
            return entry["bl_idname"]
    return type_str


def _build_node_index(node_tree) -> dict[str, Any]:
    """Build a triple-key index for O(1) node lookup.

    Maps node.name, node.bl_idname, and English display name → node.
    """
    index: dict[str, Any] = {}
    for node in node_tree.nodes:
        index[node.name] = node
        index[node.bl_idname] = node
        for eng_name, idname in _ENGLISH_NODE_NAMES.items():
            if idname == node.bl_idname:
                index[eng_name] = node
                index[eng_name.lower()] = node
    return index


def _get_node(node_tree, name_or_identifier: str, node_index: dict | None = None):
    """Get a node by name, label, or bl_idname (type) fallback.

    In localized Blender environments, default node names may differ from
    the English names that LLMs typically use.  This helper tries:
    1. Exact name match via index or nodes.get(name).
    2. Match by ``bl_idname`` (node type identifier, always English).
    3. English display-name lookup via ``_ENGLISH_NODE_NAMES`` mapping.
    """
    if node_index:
        if name_or_identifier in node_index:
            return node_index[name_or_identifier]
        bl_idname = _NAME_TO_IDNAME.get(name_or_identifier.lower())
        if bl_idname and bl_idname in node_index:
            return node_index[bl_idname]
        return None
    node = node_tree.nodes.get(name_or_identifier)
    if node:
        return node
    for node in node_tree.nodes:
        if node.bl_idname == name_or_identifier:
            return node
    bl_idname = _ENGLISH_NODE_NAMES.get(name_or_identifier)
    if bl_idname:
        for node in node_tree.nodes:
            if node.bl_idname == bl_idname:
                return node
    return None


_INDEX_SUFFIX_RE = re.compile(r"^(.+)\[(\d+)\]$")


def _find_socket(collection, ref):
    """Find a socket by name, integer index, or ``Name[N]`` suffix.

    Supports:
    - ``"Value"`` → first socket named ``Value``
    - ``0`` → socket at index 0
    - ``"Value[1]"`` → second socket named ``Value`` (0-based)
    """
    if isinstance(ref, int):
        if 0 <= ref < len(collection):
            return collection[ref]
        return None

    if not isinstance(ref, str):
        return None

    m = _INDEX_SUFFIX_RE.match(ref)
    if m:
        name, idx = m.group(1), int(m.group(2))
        candidates = [s for s in collection if s.name == name]
        if 0 <= idx < len(candidates):
            return candidates[idx]
        return None

    return collection.get(ref)


_SOCKET_TYPE_FOR_VALUE = {
    1: "VALUE",
    3: "VECTOR",
    4: "RGBA",
}


def _find_input_by_name_and_type(node, input_name: str, value: Any):
    """Find an input socket by name, preferring the one whose type matches *value*.

    Nodes like ShaderNodeMix have duplicate socket names (e.g. "A" appears as
    VALUE, VECTOR, RGBA, ROTATION).  ``inputs.get(name)`` always returns the
    first match which may be the wrong type.  This helper picks the socket
    whose Blender type aligns with the Python value being assigned.
    """
    candidates = [inp for inp in node.inputs if inp.name == input_name]
    if not candidates:
        return node.inputs.get(input_name)
    if len(candidates) == 1:
        return candidates[0]

    preferred_type = _SOCKET_TYPE_FOR_VALUE.get(len(value) if isinstance(value, (list, tuple)) else 1, None)
    if preferred_type:
        for inp in candidates:
            if inp.type == preferred_type:
                return inp

    return candidates[0]


def _resolve_node_tree_ref(value: str):
    """Resolve a string value to a NodeTree reference from bpy.data.node_groups."""
    try:
        import bpy  # type: ignore

        tree = bpy.data.node_groups.get(value)
        if tree is not None:
            return tree
    except ImportError:
        pass
    return value


def _resolve_dotted_path(root: Any, path: str) -> tuple[Any, str]:
    """Resolve a dotted property path like ``color_ramp.interpolation``.

    Returns ``(parent_object, final_attribute_name)`` so the caller can do
    ``setattr(parent, attr, value)``.

    Raises ``AttributeError`` if any intermediate segment doesn't exist.
    """
    parts = path.split(".")
    obj = root
    for part in parts[:-1]:
        obj = getattr(obj, part)
    return obj, parts[-1]


def node_tree_edit(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Edit a node tree by executing operations in order."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    tree_type = payload.get("tree_type")
    context = payload.get("context")
    operations = payload.get("operations", [])

    if not tree_type or not context:
        return _error(
            code=ErrorCode.INVALID_PARAMS,
            message="tree_type and context are required",
            started=started,
        )
    if not operations:
        return _error(
            code=ErrorCode.INVALID_PARAMS,
            message="operations array is required",
            started=started,
        )

    node_tree = _resolve_node_tree(bpy, payload)
    if node_tree is None:
        target = payload.get("target")
        # Auto-create material node tree if needed
        if tree_type == "SHADER" and context == "OBJECT" and target:
            mat = bpy.data.materials.get(target)
            if mat:
                mat.use_nodes = True
                node_tree = mat.node_tree
        if tree_type == "COMPOSITOR" and context == "SCENE":
            scene = None
            if target:
                scene = bpy.data.scenes.get(target)
            if scene is None:
                try:
                    scene = bpy.context.scene
                except (AttributeError, RuntimeError):
                    pass
            if scene:
                if not scene.use_nodes:
                    scene.use_nodes = True
                node_tree = scene.node_tree
        if tree_type == "GEOMETRY" and context == "MODIFIER" and target and "/" in target:
            obj_name, mod_name = target.split("/", 1)
            obj = bpy.data.objects.get(obj_name)
            if obj:
                mod = obj.modifiers.get(mod_name)
                if mod and mod.type == "NODES" and not mod.node_group:
                    node_group = bpy.data.node_groups.new(mod_name, "GeometryNodeTree")
                    node_group.interface.new_socket(
                        name="Geometry",
                        in_out="INPUT",
                        socket_type="NodeSocketGeometry",
                    )
                    node_group.interface.new_socket(
                        name="Geometry",
                        in_out="OUTPUT",
                        socket_type="NodeSocketGeometry",
                    )
                    node_group.nodes.new("NodeGroupInput")
                    node_group.nodes.new("NodeGroupOutput")
                    mod.node_group = node_group
                    node_tree = node_group
        if context == "NODE_GROUP" and target:
            node_tree = bpy.data.node_groups.get(target)
            if node_tree is None:
                type_map = {
                    "SHADER": "ShaderNodeTree",
                    "GEOMETRY": "GeometryNodeTree",
                    "COMPOSITOR": "CompositorNodeTree",
                }
                bl_type = type_map.get(tree_type, "ShaderNodeTree")
                node_tree = bpy.data.node_groups.new(target, bl_type)
        if node_tree is None:
            return _error(
                code=ErrorCode.NOT_FOUND,
                message=f"No node tree found for tree_type={tree_type}, context={context}",
                started=started,
            )

    node_index = _build_node_index(node_tree)

    results = []
    for i, op in enumerate(operations):
        action = op.get("action")
        try:
            if action == "add_node":
                node_type = op.get("type", "")
                resolved_type = _resolve_node_type(node_type)
                node = node_tree.nodes.new(type=resolved_type)
                if op.get("name"):
                    node.name = op["name"]
                    node.label = op["name"]
                if op.get("location"):
                    node.location = tuple(op["location"])
                node_index[node.name] = node
                node_index[node.bl_idname] = node
                results.append({"op": i, "action": "add_node", "name": node.name, "ok": True})

            elif action == "remove_node":
                node_name = op.get("name", "")
                node = _get_node(node_tree, node_name, node_index)
                if node:
                    actual_name = node.name
                    bl_idname = node.bl_idname
                    node_tree.nodes.remove(node)
                    node_index.pop(actual_name, None)
                    node_index.pop(bl_idname, None)
                    results.append(
                        {
                            "op": i,
                            "action": "remove_node",
                            "name": node_name,
                            "ok": True,
                        }
                    )
                else:
                    results.append(
                        {
                            "op": i,
                            "action": "remove_node",
                            "name": node_name,
                            "ok": False,
                            "error": "not found",
                        }
                    )

            elif action == "connect":
                from_node = _get_node(node_tree, op.get("from_node", ""), node_index)
                to_node = _get_node(node_tree, op.get("to_node", ""), node_index)
                if not from_node or not to_node:
                    results.append(
                        {
                            "op": i,
                            "action": "connect",
                            "ok": False,
                            "error": "node not found",
                        }
                    )
                    continue
                from_socket = _find_socket(from_node.outputs, op.get("from_socket", ""))
                to_socket = _find_socket(to_node.inputs, op.get("to_socket", ""))
                if not from_socket or not to_socket:
                    results.append(
                        {
                            "op": i,
                            "action": "connect",
                            "ok": False,
                            "error": "socket not found",
                        }
                    )
                    continue
                node_tree.links.new(from_socket, to_socket)
                results.append({"op": i, "action": "connect", "ok": True})

            elif action == "disconnect":
                node_name = op.get("node", "")
                input_name = op.get("input", "")
                node = _get_node(node_tree, node_name, node_index)
                if node:
                    inp = _find_socket(node.inputs, input_name)
                    if inp and inp.links:
                        for link in list(inp.links):
                            node_tree.links.remove(link)
                        results.append({"op": i, "action": "disconnect", "ok": True})
                    else:
                        results.append(
                            {
                                "op": i,
                                "action": "disconnect",
                                "ok": False,
                                "error": "no link found",
                            }
                        )
                else:
                    results.append(
                        {
                            "op": i,
                            "action": "disconnect",
                            "ok": False,
                            "error": "node not found",
                        }
                    )

            elif action == "set_value":
                node_name = op.get("node", "")
                input_name = op.get("input", "")
                value = op.get("value")
                node = _get_node(node_tree, node_name, node_index)
                if node:
                    inp = _find_input_by_name_and_type(node, input_name, value)
                    if inp and hasattr(inp, "default_value"):
                        try:
                            coerced = coerce_value(value, inp.default_value)
                            inp.default_value = coerced
                            results.append({"op": i, "action": "set_value", "ok": True})
                        except (TypeError, ValueError) as exc:
                            results.append(
                                {
                                    "op": i,
                                    "action": "set_value",
                                    "ok": False,
                                    "error": str(exc),
                                }
                            )
                    else:
                        results.append(
                            {
                                "op": i,
                                "action": "set_value",
                                "ok": False,
                                "error": "input not found",
                            }
                        )
                else:
                    results.append(
                        {
                            "op": i,
                            "action": "set_value",
                            "ok": False,
                            "error": "node not found",
                        }
                    )

            elif action == "set_property":
                node_name = op.get("node", "")
                prop_name = op.get("property", "")
                value = op.get("value")
                node = _get_node(node_tree, node_name, node_index)
                if not node:
                    results.append(
                        {"op": i, "action": "set_property", "ok": False, "error": "node not found"}
                    )
                else:
                    try:
                        target_obj, final_attr = _resolve_dotted_path(node, prop_name)
                    except AttributeError:
                        results.append(
                            {
                                "op": i,
                                "action": "set_property",
                                "ok": False,
                                "error": f"property path '{prop_name}' not found",
                            }
                        )
                        continue

                    if not hasattr(target_obj, final_attr):
                        results.append(
                            {
                                "op": i,
                                "action": "set_property",
                                "ok": False,
                                "error": f"property '{final_attr}' not found on {type(target_obj).__name__}",
                            }
                        )
                        continue

                    current = getattr(target_obj, final_attr)
                    if current is None and isinstance(value, str) and prop_name in ("node_tree",):
                        coerced = _resolve_node_tree_ref(value)
                    else:
                        coerced = coerce_value(value, current)
                    setattr(target_obj, final_attr, coerced)
                    results.append({"op": i, "action": "set_property", "ok": True})

            elif action == "set_color_ramp_element":
                node_name = op.get("node", "")
                element_index = op.get("index", 0)
                position = op.get("position")
                color = op.get("color")
                node = _get_node(node_tree, node_name, node_index)
                if node and hasattr(node, "color_ramp"):
                    elements = node.color_ramp.elements
                    if 0 <= element_index < len(elements):
                        element = elements[element_index]
                        if position is not None:
                            element.position = float(position)
                        if color is not None:
                            element.color = tuple(color)
                        results.append(
                            {
                                "op": i,
                                "action": "set_color_ramp_element",
                                "index": element_index,
                                "position": element.position,
                                "color": list(element.color),
                                "ok": True,
                            }
                        )
                    else:
                        results.append(
                            {
                                "op": i,
                                "action": "set_color_ramp_element",
                                "ok": False,
                                "error": f"element index {element_index} out of range (0-{len(elements)-1})",
                            }
                        )
                else:
                    results.append(
                        {
                            "op": i,
                            "action": "set_color_ramp_element",
                            "ok": False,
                            "error": "node not found or has no color_ramp",
                        }
                    )

            elif action == "add_color_ramp_element":
                node_name = op.get("node", "")
                position = op.get("position", 0.5)
                color = op.get("color")
                node = _get_node(node_tree, node_name, node_index)
                if node and hasattr(node, "color_ramp"):
                    new_elem = node.color_ramp.elements.new(float(position))
                    if color is not None:
                        new_elem.color = tuple(color)
                    results.append(
                        {
                            "op": i,
                            "action": "add_color_ramp_element",
                            "index": list(node.color_ramp.elements).index(new_elem),
                            "position": new_elem.position,
                            "color": list(new_elem.color),
                            "ok": True,
                        }
                    )
                else:
                    results.append(
                        {
                            "op": i,
                            "action": "add_color_ramp_element",
                            "ok": False,
                            "error": "node not found or has no color_ramp",
                        }
                    )

            elif action == "remove_color_ramp_element":
                node_name = op.get("node", "")
                element_index = op.get("index", 0)
                node = _get_node(node_tree, node_name, node_index)
                if node and hasattr(node, "color_ramp"):
                    elements = node.color_ramp.elements
                    if len(elements) <= 1:
                        results.append(
                            {
                                "op": i,
                                "action": "remove_color_ramp_element",
                                "ok": False,
                                "error": "cannot remove last element",
                            }
                        )
                    elif 0 <= element_index < len(elements):
                        node.color_ramp.elements.remove(elements[element_index])
                        results.append(
                            {"op": i, "action": "remove_color_ramp_element", "index": element_index, "ok": True}
                        )
                    else:
                        results.append(
                            {
                                "op": i,
                                "action": "remove_color_ramp_element",
                                "ok": False,
                                "error": f"element index {element_index} out of range (0-{len(elements)-1})",
                            }
                        )
                else:
                    results.append(
                        {
                            "op": i,
                            "action": "remove_color_ramp_element",
                            "ok": False,
                            "error": "node not found or has no color_ramp",
                        }
                    )

            elif action == "set_curve_mapping_point":
                node_name = op.get("node", "")
                curve_index = op.get("curve_index", 0)
                point_index = op.get("point_index", 0)
                location = op.get("location")
                handle_type = op.get("handle_type")
                node = _get_node(node_tree, node_name, node_index)
                if node and hasattr(node, "mapping"):
                    mapping = node.mapping
                    if 0 <= curve_index < len(mapping.curves):
                        curve = mapping.curves[curve_index]
                        if 0 <= point_index < len(curve.points):
                            point = curve.points[point_index]
                            if location is not None:
                                point.location = tuple(location)
                            if handle_type is not None:
                                point.handle_type = handle_type
                            mapping.update()
                            results.append(
                                {
                                    "op": i,
                                    "action": "set_curve_mapping_point",
                                    "curve_index": curve_index,
                                    "point_index": point_index,
                                    "location": list(point.location),
                                    "ok": True,
                                }
                            )
                        else:
                            results.append(
                                {
                                    "op": i,
                                    "action": "set_curve_mapping_point",
                                    "ok": False,
                                    "error": f"point_index {point_index} out of range",
                                }
                            )
                    else:
                        results.append(
                            {
                                "op": i,
                                "action": "set_curve_mapping_point",
                                "ok": False,
                                "error": f"curve_index {curve_index} out of range",
                            }
                        )
                else:
                    results.append(
                        {
                            "op": i,
                            "action": "set_curve_mapping_point",
                            "ok": False,
                            "error": "node not found or has no mapping",
                        }
                    )

            elif action == "add_interface_socket":
                socket_name = op.get("name", "Value")
                in_out = op.get("in_out", "INPUT")
                socket_type = op.get("socket_type", "NodeSocketFloat")
                try:
                    node_tree.interface.new_socket(
                        name=socket_name,
                        in_out=in_out,
                        socket_type=socket_type,
                    )
                    results.append({"op": i, "action": "add_interface_socket", "name": socket_name, "ok": True})
                except (AttributeError, TypeError) as exc:
                    results.append(
                        {
                            "op": i,
                            "action": "add_interface_socket",
                            "ok": False,
                            "error": str(exc),
                        }
                    )

            elif action == "remove_interface_socket":
                socket_name = op.get("socket_name", op.get("name", ""))
                found = False
                for item in node_tree.interface.items_tree:
                    if item.item_type == "SOCKET" and item.name == socket_name:
                        node_tree.interface.remove(item)
                        found = True
                        break
                if found:
                    results.append({"op": i, "action": "remove_interface_socket", "name": socket_name, "ok": True})
                else:
                    results.append(
                        {
                            "op": i,
                            "action": "remove_interface_socket",
                            "ok": False,
                            "error": "socket not found",
                        }
                    )

            else:
                results.append(
                    {
                        "op": i,
                        "action": action,
                        "ok": False,
                        "error": f"unknown action: {action}",
                    }
                )

        except (AttributeError, KeyError, TypeError, RuntimeError, ValueError) as exc:
            results.append({"op": i, "action": action, "ok": False, "error": str(exc)})

    success_count = sum(1 for r in results if r.get("ok"))
    return _ok(
        result={
            "tree_name": node_tree.name,
            "operations_total": len(operations),
            "operations_succeeded": success_count,
            "operations_failed": len(operations) - success_count,
            "details": results,
        },
        started=started,
    )
