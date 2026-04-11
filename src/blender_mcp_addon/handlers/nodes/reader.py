# -*- coding: utf-8 -*-
"""Node tree reader — reads shader, compositor, and geometry node trees."""

from __future__ import annotations

from typing import Any

from ..response import _ok, _error, check_bpy_available, bpy_unavailable_error


def _read_node(node: Any, depth: str) -> dict[str, Any]:
    """Read a single node's data."""
    data: dict[str, Any] = {
        "name": node.name,
        "type": node.bl_idname,
        "label": node.label or node.name,
        "location": [node.location.x, node.location.y],
    }
    if depth == "full":
        inputs = []
        for inp in node.inputs:
            inp_data: dict[str, Any] = {"name": inp.name, "type": inp.type}
            if hasattr(inp, "default_value"):
                try:
                    val = inp.default_value
                    if hasattr(val, "__len__") and not isinstance(val, str):
                        inp_data["value"] = list(val)
                    else:
                        inp_data["value"] = val
                except Exception:
                    inp_data["value"] = "<unreadable>"
            inp_data["is_linked"] = inp.is_linked
            inputs.append(inp_data)
        data["inputs"] = inputs

        outputs = []
        for out in node.outputs:
            outputs.append(
                {"name": out.name, "type": out.type, "is_linked": out.is_linked}
            )
        data["outputs"] = outputs
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
        scene = bpy.data.scenes.get(target) if target else bpy.context.scene
        if scene:
            if not scene.use_nodes:
                scene.use_nodes = True
            if scene.use_nodes and scene.node_tree:
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
            code="invalid_params",
            message="tree_type and context are required",
            started=started,
        )

    node_tree = _resolve_node_tree(bpy, payload)
    if node_tree is None:
        return _error(
            code="not_found",
            message=f"No node tree found for tree_type={tree_type}, context={context}, target={payload.get('target')}",
            started=started,
        )

    depth = payload.get("depth", "summary")
    nodes = [_read_node(n, depth) for n in node_tree.nodes]
    links = [_read_link(l) for l in node_tree.links] if depth == "full" else []

    return _ok(
        result={
            "tree_name": node_tree.name,
            "tree_type": tree_type,
            "context": context,
            "node_count": len(node_tree.nodes),
            "link_count": len(node_tree.links),
            "nodes": nodes,
            "links": links,
        },
        started=started,
    )
