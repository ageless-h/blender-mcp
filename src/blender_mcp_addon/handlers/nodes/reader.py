# -*- coding: utf-8 -*-
"""Node tree reader — reads shader, compositor, and geometry node trees."""

from __future__ import annotations

from typing import Any

from ..error_codes import ErrorCode
from ..response import _error, _ok, bpy_unavailable_error, check_bpy_available

# ---------------------------------------------------------------------------
# Helpers: node-specific property reading via Blender RNA introspection
# ---------------------------------------------------------------------------

# Cached set of base-Node property identifiers (populated on first use).
_BASE_NODE_PROPS: frozenset[str] | None = None

# Properties to skip even if not in the base Node class (handled elsewhere).
_EXTRA_SKIP_PROPS = frozenset({"node_tree"})


def _get_base_node_props() -> frozenset[str]:
    """Return identifiers of properties inherited from the base Node class."""
    global _BASE_NODE_PROPS
    if _BASE_NODE_PROPS is not None:
        return _BASE_NODE_PROPS
    try:
        import bpy  # type: ignore

        _BASE_NODE_PROPS = frozenset(p.identifier for p in bpy.types.Node.bl_rna.properties)
    except ImportError:
        # Fallback for unit-test environments without bpy.
        _BASE_NODE_PROPS = frozenset({
            "bl_description", "bl_height_default", "bl_height_max", "bl_height_min",
            "bl_icon", "bl_idname", "bl_label", "bl_static_type",
            "bl_width_default", "bl_width_max", "bl_width_min",
            "color", "dimensions", "height", "hide", "internal_links",
            "inputs", "label", "location", "mute", "name", "outputs",
            "parent", "rna_type", "select", "show_options", "show_preview",
            "show_texture", "type", "use_custom_color", "width", "width_hidden",
        })
    return _BASE_NODE_PROPS


def _serialize_color_ramp(color_ramp: Any) -> dict[str, Any]:
    """Serialize a ``ColorRamp`` to a JSON-safe dict."""
    elements = []
    for elem in color_ramp.elements:
        elements.append({
            "position": round(elem.position, 5),
            "color": [round(c, 5) for c in elem.color],
        })
    return {
        "interpolation": color_ramp.interpolation,
        "color_mode": color_ramp.color_mode,
        "hue_interpolation": color_ramp.hue_interpolation,
        "elements": elements,
    }


def _serialize_curve_mapping(mapping: Any) -> dict[str, Any]:
    """Serialize a ``CurveMapping`` to a JSON-safe dict."""
    curves = []
    for curve in mapping.curves:
        points = []
        for point in curve.points:
            points.append({
                "location": [round(v, 5) for v in point.location],
                "handle_type": point.handle_type,
            })
        curves.append({"points": points})
    return {
        "use_clip": mapping.use_clip,
        "clip_min_x": mapping.clip_min_x,
        "clip_min_y": mapping.clip_min_y,
        "clip_max_x": mapping.clip_max_x,
        "clip_max_y": mapping.clip_max_y,
        "curves": curves,
    }


def _serialize_prop_value(node: Any, prop: Any) -> Any:
    """Serialize a single RNA property value to a JSON-safe value.

    Returns ``None`` for unsupported or unreadable properties.
    """
    try:
        value = getattr(node, prop.identifier)
    except (AttributeError, RuntimeError):
        return None
    if value is None:
        return None

    # -- Pointer properties --------------------------------------------------
    if prop.type == "POINTER":
        type_name = type(value).__name__
        if type_name == "ColorRamp":
            return _serialize_color_ramp(value)
        if type_name == "CurveMapping":
            return _serialize_curve_mapping(value)
        if type_name == "Image":
            info: dict[str, Any] = {"name": value.name}
            if hasattr(value, "filepath") and value.filepath:
                info["filepath"] = value.filepath
            return info
        # Other named data-block references → return name only.
        if hasattr(value, "name"):
            return value.name
        return None

    # -- Simple types --------------------------------------------------------
    if prop.type in ("ENUM", "INT", "FLOAT", "BOOLEAN", "STRING"):
        return value

    return None


def _read_node_properties(node: Any) -> dict[str, Any]:
    """Read node-specific RNA properties (excludes base-Node & socket data).

    Iterates over ``node.bl_rna.properties`` and returns a dict of
    *property-identifier* → *serialised value* for all non-base,
    user-relevant properties.  Readonly POINTER properties (e.g.
    ``color_ramp``, ``mapping``) are included because their *content*
    is mutable even though the pointer itself is not.
    """
    base_props = _get_base_node_props() | _EXTRA_SKIP_PROPS
    properties: dict[str, Any] = {}

    try:
        rna_props = node.bl_rna.properties
    except AttributeError:
        return properties

    for prop in rna_props:
        if prop.identifier in base_props:
            continue

        # POINTER: always try (even when readonly, e.g. color_ramp).
        if prop.type == "POINTER":
            value = _serialize_prop_value(node, prop)
            if value is not None:
                properties[prop.identifier] = value
            continue

        # Skip readonly simple properties and collections.
        if prop.is_readonly or prop.type == "COLLECTION":
            continue

        value = _serialize_prop_value(node, prop)
        if value is not None:
            properties[prop.identifier] = value

    return properties


# ---------------------------------------------------------------------------
# Main node reader
# ---------------------------------------------------------------------------


def _read_node(
    node: Any,
    depth: str,
    expand_groups: bool = False,
    max_depth: int = 3,
    skip_defaults: bool = True,
    _current_depth: int = 0,
) -> dict[str, Any]:
    """Read a single node's data.

    Args:
        node: The Blender node to read
        depth: 'summary', 'topology', or 'full' - controls level of detail
        expand_groups: If True, recursively expand node groups
        max_depth: Maximum recursion depth for group expansion
        skip_defaults: If True, skip inputs with default values (for 'topology'/'full')
        _current_depth: Internal counter for recursion depth
    """
    data: dict[str, Any] = {
        "name": node.name,
        "type": node.bl_idname,
    }

    if node.label and node.label != node.name:
        data["label"] = node.label

    if depth == "full":
        data["location"] = [node.location.x, node.location.y]

    if node.type == "GROUP":
        data["is_group"] = True
        if hasattr(node, "node_tree") and node.node_tree:
            data["group_tree_name"] = node.node_tree.name

    if depth in ("topology", "full"):
        inputs = []
        for inp in node.inputs:
            if depth == "topology":
                if not inp.is_linked and skip_defaults:
                    continue
                inp_data: dict[str, Any] = {"name": inp.name}
                if inp.is_linked:
                    inp_data["is_linked"] = True
                else:
                    if hasattr(inp, "default_value"):
                        try:
                            val = inp.default_value
                            if hasattr(val, "__len__") and not isinstance(val, str):
                                inp_data["value"] = [round(v, 4) for v in val]
                            else:
                                inp_data["value"] = round(val, 4) if isinstance(val, float) else val
                        except (AttributeError, ValueError):
                            pass
            else:
                inp_data = {"name": inp.name, "type": inp.type}
                if hasattr(inp, "default_value"):
                    try:
                        val = inp.default_value
                        if hasattr(val, "__len__") and not isinstance(val, str):
                            inp_data["value"] = [round(v, 4) for v in val] if skip_defaults else list(val)
                        else:
                            inp_data["value"] = round(val, 4) if isinstance(val, float) else val
                    except (AttributeError, ValueError):
                        inp_data["value"] = "<unreadable>"
                inp_data["is_linked"] = inp.is_linked
            inputs.append(inp_data)
        if inputs:
            data["inputs"] = inputs

        outputs = []
        for out in node.outputs:
            if depth == "topology":
                if not out.is_linked:
                    continue
                outputs.append({"name": out.name})
            else:
                outputs.append({"name": out.name, "type": out.type, "is_linked": out.is_linked})
        if outputs:
            data["outputs"] = outputs

    if depth == "full":
        props = _read_node_properties(node)
        if props:
            data["properties"] = props

    if (
        expand_groups
        and node.type == "GROUP"
        and hasattr(node, "node_tree")
        and node.node_tree
        and _current_depth < max_depth
    ):
        internal_tree = node.node_tree
        data["internal_tree"] = {
            "name": internal_tree.name,
            "nodes": [
                _read_node(n, depth, expand_groups, max_depth, skip_defaults, _current_depth + 1)
                for n in internal_tree.nodes
            ],
            "links": [_read_link(l) for l in internal_tree.links] if depth in ("topology", "full") else [],
        }

    return data


def _read_link(link: Any) -> dict[str, Any]:
    """Read a single link's data."""
    return {
        "from_node": link.from_node.name,
        "from_socket": link.from_socket.name,
        "to_node": link.to_node.name,
        "to_socket": link.to_socket.name,
    }


def _resolve_node_tree(bpy: Any, payload: dict[str, Any]) -> Any:
    """Resolve the target node tree from tree_type + context + target."""
    tree_type = payload.get("tree_type", "SHADER")
    context = payload.get("context", "OBJECT")
    target = payload.get("target")

    if tree_type == "SHADER":
        if context == "OBJECT":
            mat = bpy.data.materials.get(target) if target else None
            if mat is None and target:
                return None
            if mat is None:
                obj = bpy.context.active_object
                if obj and obj.active_material:
                    mat = obj.active_material
            if mat and mat.use_nodes:
                return mat.node_tree
            return None
        elif context == "WORLD":
            world = bpy.data.worlds.get(target) if target else bpy.context.scene.world
            if world and world.use_nodes:
                return world.node_tree
            return None
        elif context == "LINESTYLE":
            if target and hasattr(bpy.data, "linestyles"):
                ls = bpy.data.linestyles.get(target)
                if ls and ls.use_nodes:
                    return ls.node_tree
            return None

    elif tree_type == "COMPOSITOR":
        scene = None
        if target:
            scene = bpy.data.scenes.get(target)
        if scene is None:
            try:
                scene = bpy.context.scene
            except (AttributeError, RuntimeError):
                pass
        if scene:
            use_nodes = False
            try:
                use_nodes = scene.use_nodes
            except (AttributeError, RuntimeError):
                pass
            if not use_nodes:
                try:
                    scene.use_nodes = True
                except (AttributeError, RuntimeError):
                    pass
            try:
                use_nodes = scene.use_nodes
            except (AttributeError, RuntimeError):
                pass
            if use_nodes and scene.node_tree:
                return scene.node_tree
        return None

    elif tree_type == "GEOMETRY":
        if context == "MODIFIER" and target and "/" in target:
            obj_name, mod_name = target.split("/", 1)
            obj = bpy.data.objects.get(obj_name)
            if obj:
                mod = obj.modifiers.get(mod_name)
                if mod and mod.type == "NODES" and mod.node_group:
                    return mod.node_group
        return None

    if context == "NODE_GROUP" and target:
        node_tree = bpy.data.node_groups.get(target)
        if node_tree:
            return node_tree

    return None


def node_tree_read(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Read a node tree structure."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    tree_type = payload.get("tree_type")
    context = payload.get("context")
    if not tree_type or not context:
        return _error(
            code=ErrorCode.INVALID_PARAMS,
            message="tree_type and context are required",
            started=started,
        )

    node_tree = _resolve_node_tree(bpy, payload)
    if node_tree is None:
        return _error(
            code=ErrorCode.NOT_FOUND,
            message=f"No node tree found for tree_type={tree_type}, context={context}, target={payload.get('target')}",
            started=started,
        )

    depth = payload.get("depth", "summary")
    expand_groups = bool(payload.get("expand_groups", False))
    max_depth = int(payload.get("max_depth", 3))
    skip_defaults = bool(payload.get("skip_defaults", True))

    nodes = [_read_node(n, depth, expand_groups, max_depth, skip_defaults) for n in node_tree.nodes]
    links = [_read_link(l) for l in node_tree.links] if depth in ("topology", "full") else []

    result = {
        "tree_name": node_tree.name,
        "tree_type": tree_type,
        "context": context,
        "nodes": nodes,
    }

    if links:
        result["links"] = links

    return _ok(result=result, started=started)
