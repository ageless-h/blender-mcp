# -*- coding: utf-8 -*-
"""Mesh handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..registry import HandlerRegistry
from ..shared import create_mesh_primitive, link_data_to_scene
from ..types import DataType


@HandlerRegistry.register
class MeshHandler(BaseHandler):
    """Handler for Blender mesh data type (bpy.data.meshes)."""

    data_type = DataType.MESH

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new mesh.

        Args:
            name: Name for the new mesh
            params: Creation parameters:
                - primitive/type: Type of primitive (cube, sphere, plane, cylinder, etc.)
                - size: Size for primitives
                - radius/depth/segments: Cylinder/cone parameters
                - vertices: List of vertex coordinates
                - edges: List of edge indices
                - faces: List of face vertex indices

        Returns:
            Dict with created mesh info
        """
        import bpy  # type: ignore

        mesh = bpy.data.meshes.new(name=name)

        primitive = params.get("primitive") or params.get("type")
        if primitive:
            create_mesh_primitive(mesh, primitive, params)

        vertices = params.get("vertices")
        edges = params.get("edges")
        faces = params.get("faces")

        if vertices is not None:
            mesh.from_pydata(vertices, edges if edges else [], faces if faces else [])
            mesh.validate()
            mesh.update()

        result = {
            "name": mesh.name,
            "type": "mesh",
            "geometry_type": primitive.lower() if isinstance(primitive, str) else None,
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
        }

        if params.get("link_object", False):
            obj = link_data_to_scene(mesh, params)
            result["object_name"] = obj.name

        return result

    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read mesh properties.

        Args:
            name: Name of the mesh
            path: Optional property path
            params: Read parameters:
                - evaluated: If True, read with modifiers applied (needs object name)
                - include_vertices: Include vertex data
                - include_faces: Include face data

        Returns:
            Dict with mesh properties
        """
        import bpy  # type: ignore

        mesh = bpy.data.meshes.get(name)
        if mesh is None:
            raise KeyError(f"Mesh '{name}' not found")

        if path:
            value = self._get_nested_attr(mesh, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            return {"name": name, "path": path, "value": value}

        evaluated = params.get("evaluated", False)
        obj_eval = None
        if evaluated:
            object_name = params.get("object")
            if object_name:
                obj = bpy.data.objects.get(object_name)
                if obj:
                    depsgraph = bpy.context.evaluated_depsgraph_get()
                    obj_eval = obj.evaluated_get(depsgraph)

        try:
            if obj_eval is not None:
                mesh = obj_eval.to_mesh()

            result = {
                "name": mesh.name,
                "vertices_count": len(mesh.vertices),
                "edges_count": len(mesh.edges),
                "polygons_count": len(mesh.polygons),
                "loops_count": len(mesh.loops),
                "has_custom_normals": mesh.has_custom_normals,
                "is_editmode": mesh.is_editmode,
                "materials": [m.name if m else None for m in mesh.materials],
            }

            if params.get("include_vertices"):
                result["vertices"] = [list(v.co) for v in mesh.vertices]

            if params.get("include_faces"):
                result["faces"] = [list(p.vertices) for p in mesh.polygons]

            return result
        finally:
            if obj_eval is not None:
                obj_eval.to_mesh_clear()

    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write properties to a mesh.

        Args:
            name: Name of the mesh
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        mesh = bpy.data.meshes.get(name)
        if mesh is None:
            raise KeyError(f"Mesh '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            if prop_path == "vertices":
                for i, co in enumerate(value):
                    if i < len(mesh.vertices):
                        mesh.vertices[i].co = tuple(co)
                modified.append("vertices")
            else:
                self._set_nested_attr(mesh, prop_path, value)
                modified.append(prop_path)

        mesh.update()
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a mesh.

        Args:
            name: Name of the mesh to delete
            params: Deletion parameters

        Returns:
            Dict with deleted mesh name
        """
        import bpy  # type: ignore

        mesh = bpy.data.meshes.get(name)
        if mesh is None:
            raise KeyError(f"Mesh '{name}' not found")

        bpy.data.meshes.remove(mesh)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all meshes.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = []
        for mesh in bpy.data.meshes:
            items.append(
                {
                    "name": mesh.name,
                    "vertices": len(mesh.vertices),
                    "polygons": len(mesh.polygons),
                    "users": mesh.users,
                }
            )

        return {"items": items, "count": len(items)}
