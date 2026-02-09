# -*- coding: utf-8 -*-
"""Node tree editor — add/remove nodes, connect/disconnect, set values."""
from __future__ import annotations

import logging
from typing import Any

from ..response import _ok, _error, check_bpy_available, bpy_unavailable_error
from .reader import _resolve_node_tree

logger = logging.getLogger(__name__)


def _get_node(node_tree, name_or_identifier: str):
    """Get a node by name, label, or bl_idname (type) fallback.

    In localized Blender environments, default node names may differ from
    the English names that LLMs typically use.  This helper tries:
    1. Exact name match  (``nodes.get(name)``).
    2. Match by ``bl_idname`` (node type identifier, always English).
    """
    node = node_tree.nodes.get(name_or_identifier)
    if node:
        return node
    for node in node_tree.nodes:
        if node.bl_idname == name_or_identifier:
            return node
    return None


def node_tree_edit(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Edit a node tree by executing operations in order."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    tree_type = payload.get("tree_type")
    context = payload.get("context")
    operations = payload.get("operations", [])

    if not tree_type or not context:
        return _error(code="invalid_params", message="tree_type and context are required", started=started)
    if not operations:
        return _error(code="invalid_params", message="operations array is required", started=started)

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
            scene = bpy.data.scenes.get(target) if target else bpy.context.scene
            if scene:
                scene.use_nodes = True
                node_tree = scene.node_tree
        if tree_type == "GEOMETRY" and context == "MODIFIER" and target and "/" in target:
            obj_name, mod_name = target.split("/", 1)
            obj = bpy.data.objects.get(obj_name)
            if obj:
                mod = obj.modifiers.get(mod_name)
                if mod and mod.type == "NODES" and not mod.node_group:
                    node_group = bpy.data.node_groups.new(mod_name, "GeometryNodeTree")
                    node_group.nodes.new("NodeGroupInput")
                    node_group.nodes.new("NodeGroupOutput")
                    mod.node_group = node_group
                    node_tree = node_group
        if node_tree is None:
            return _error(
                code="not_found",
                message=f"No node tree found for tree_type={tree_type}, context={context}",
                started=started,
            )

    results = []
    for i, op in enumerate(operations):
        action = op.get("action")
        try:
            if action == "add_node":
                node_type = op.get("type", "")
                node = node_tree.nodes.new(type=node_type)
                if op.get("name"):
                    node.name = op["name"]
                    node.label = op["name"]
                if op.get("location"):
                    node.location = tuple(op["location"])
                results.append({"op": i, "action": "add_node", "name": node.name, "ok": True})

            elif action == "remove_node":
                node_name = op.get("name", "")
                node = _get_node(node_tree, node_name)
                if node:
                    node_tree.nodes.remove(node)
                    results.append({"op": i, "action": "remove_node", "name": node_name, "ok": True})
                else:
                    results.append({"op": i, "action": "remove_node", "name": node_name, "ok": False, "error": "not found"})

            elif action == "connect":
                from_node = _get_node(node_tree, op.get("from_node", ""))
                to_node = _get_node(node_tree, op.get("to_node", ""))
                if not from_node or not to_node:
                    results.append({"op": i, "action": "connect", "ok": False, "error": "node not found"})
                    continue
                from_socket = from_node.outputs.get(op.get("from_socket", ""))
                to_socket = to_node.inputs.get(op.get("to_socket", ""))
                if not from_socket or not to_socket:
                    results.append({"op": i, "action": "connect", "ok": False, "error": "socket not found"})
                    continue
                node_tree.links.new(from_socket, to_socket)
                results.append({"op": i, "action": "connect", "ok": True})

            elif action == "disconnect":
                node_name = op.get("node", "")
                input_name = op.get("input", "")
                node = _get_node(node_tree, node_name)
                if node:
                    inp = node.inputs.get(input_name)
                    if inp and inp.links:
                        for link in list(inp.links):
                            node_tree.links.remove(link)
                        results.append({"op": i, "action": "disconnect", "ok": True})
                    else:
                        results.append({"op": i, "action": "disconnect", "ok": False, "error": "no link found"})
                else:
                    results.append({"op": i, "action": "disconnect", "ok": False, "error": "node not found"})

            elif action == "set_value":
                node_name = op.get("node", "")
                input_name = op.get("input", "")
                value = op.get("value")
                node = _get_node(node_tree, node_name)
                if node:
                    inp = node.inputs.get(input_name)
                    if inp and hasattr(inp, "default_value"):
                        if isinstance(value, list):
                            inp.default_value = type(inp.default_value)(value)
                        else:
                            inp.default_value = value
                        results.append({"op": i, "action": "set_value", "ok": True})
                    else:
                        results.append({"op": i, "action": "set_value", "ok": False, "error": "input not found"})
                else:
                    results.append({"op": i, "action": "set_value", "ok": False, "error": "node not found"})

            elif action == "set_property":
                node_name = op.get("node", "")
                prop_name = op.get("property", "")
                value = op.get("value")
                node = _get_node(node_tree, node_name)
                if node and hasattr(node, prop_name):
                    setattr(node, prop_name, value)
                    results.append({"op": i, "action": "set_property", "ok": True})
                else:
                    results.append({"op": i, "action": "set_property", "ok": False, "error": "node or property not found"})

            else:
                results.append({"op": i, "action": action, "ok": False, "error": f"unknown action: {action}"})

        except Exception as exc:
            results.append({"op": i, "action": action, "ok": False, "error": str(exc)})

    success_count = sum(1 for r in results if r.get("ok"))
    return _ok(result={
        "tree_name": node_tree.name,
        "operations_total": len(operations),
        "operations_succeeded": success_count,
        "operations_failed": len(operations) - success_count,
        "details": results,
    }, started=started)
