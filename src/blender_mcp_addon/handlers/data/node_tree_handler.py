# -*- coding: utf-8 -*-
"""Node tree handler for unified CRUD operations."""
from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class NodeTreeHandler(BaseHandler):
    """Handler for Blender node tree data type (bpy.data.node_groups)."""

    data_type = DataType.NODE_TREE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new node tree.

        Args:
            name: Name for the new node tree
            params: Creation parameters:
                - type: Node tree type (GeometryNodeTree, ShaderNodeTree, CompositorNodeTree)

        Returns:
            Dict with created node tree info
        """
        import bpy  # type: ignore

        tree_type = params.get("type", "GeometryNodeTree")
        node_tree = bpy.data.node_groups.new(name=name, type=tree_type)

        return {
            "name": node_tree.name,
            "type": "node_tree",
            "tree_type": node_tree.bl_idname,
        }

    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read node tree properties.

        Args:
            name: Name of the node tree
            path: Optional property path
            params: Read parameters:
                - include_nodes: Include node list (default: False)
                - include_links: Include link list (default: False)

        Returns:
            Dict with node tree properties
        """
        import bpy  # type: ignore

        node_tree = bpy.data.node_groups.get(name)
        if node_tree is None:
            raise KeyError(f"Node tree '{name}' not found")

        if path:
            value = self._get_nested_attr(node_tree, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            return {"name": name, "path": path, "value": value}

        result: dict[str, Any] = {
            "name": node_tree.name,
            "tree_type": node_tree.bl_idname,
            "nodes": len(node_tree.nodes),
            "links": len(node_tree.links),
            "users": node_tree.users,
        }

        if params.get("include_nodes", False):
            nodes_info = []
            for node in node_tree.nodes:
                node_info: dict[str, Any] = {
                    "name": node.name,
                    "type": node.type,
                }
                if node.label and node.label != node.name:
                    node_info["label"] = node.label
                nodes_info.append(node_info)
            result["node_list"] = nodes_info

        if params.get("include_links", False):
            links_info = []
            for link in node_tree.links:
                links_info.append({
                    "from_node": link.from_node.name,
                    "from_socket": link.from_socket.name,
                    "to_node": link.to_node.name,
                    "to_socket": link.to_socket.name,
                })
            result["link_list"] = links_info

        return result

    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write properties to a node tree.

        Args:
            name: Name of the node tree
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        node_tree = bpy.data.node_groups.get(name)
        if node_tree is None:
            raise KeyError(f"Node tree '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            if prop_path == "add_node":
                node_type = value.get("type")
                node_name = value.get("name")
                location = value.get("location", (0, 0))
                new_node = node_tree.nodes.new(type=node_type)
                if node_name:
                    new_node.name = node_name
                new_node.location = tuple(location)
                modified.append(f"add_node:{new_node.name}")
            elif prop_path == "add_link":
                from_node = node_tree.nodes.get(value.get("from_node"))
                to_node = node_tree.nodes.get(value.get("to_node"))
                if from_node and to_node:
                    from_socket = from_node.outputs.get(value.get("from_socket"))
                    to_socket = to_node.inputs.get(value.get("to_socket"))
                    if from_socket and to_socket:
                        node_tree.links.new(from_socket, to_socket)
                        modified.append("add_link")
            else:
                self._set_nested_attr(node_tree, prop_path, value)
                modified.append(prop_path)

        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a node tree.

        Args:
            name: Name of the node tree to delete
            params: Deletion parameters

        Returns:
            Dict with deleted node tree name
        """
        import bpy  # type: ignore

        node_tree = bpy.data.node_groups.get(name)
        if node_tree is None:
            raise KeyError(f"Node tree '{name}' not found")

        bpy.data.node_groups.remove(node_tree)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all node trees.

        Args:
            filter_params: Optional filter criteria:
                - tree_type: Filter by tree type

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        filter_params = filter_params or {}
        tree_type = filter_params.get("tree_type")

        items = []
        for node_tree in bpy.data.node_groups:
            if tree_type and node_tree.bl_idname != tree_type:
                continue
            items.append({
                "name": node_tree.name,
                "tree_type": node_tree.bl_idname,
                "nodes": len(node_tree.nodes),
                "users": node_tree.users,
            })

        return {"items": items}

    def link(
        self,
        source_name: str,
        target_type: DataType,
        target_name: str,
        unlink: bool = False,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Link/unlink node tree to a modifier (e.g., GeometryNodes).

        Expected target: modifier on an object. Params must include object name.
        """
        import bpy  # type: ignore

        if target_type != DataType.MODIFIER:
            return {"error": f"NodeTree can only be linked to modifiers, not {target_type.value}"}

        params = params or {}
        object_name = params.get("object") or params.get("target_object")
        if not object_name:
            return {"error": "'object' parameter is required to link node_tree to modifier"}

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")

        modifier = obj.modifiers.get(target_name)
        if modifier is None:
            raise KeyError(f"Modifier '{target_name}' not found on object '{object_name}'")

        node_tree = bpy.data.node_groups.get(source_name)
        if node_tree is None:
            raise KeyError(f"NodeTree '{source_name}' not found")

        if unlink:
            if getattr(modifier, "node_group", None) == node_tree:
                modifier.node_group = None
                return {"action": "unlink", "node_tree": source_name, "modifier": target_name, "object": object_name}
            return {"action": "unlink", "skipped": True, "reason": "Modifier not linked to node tree"}

        modifier.node_group = node_tree
        return {"action": "link", "node_tree": source_name, "modifier": target_name, "object": object_name}
