# -*- coding: utf-8 -*-
"""Mesh handler for unified CRUD operations."""
from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class MeshHandler(BaseHandler):
    """Handler for Blender mesh data type (bpy.data.meshes)."""
    
    data_type = DataType.MESH
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new mesh.
        
        Args:
            name: Name for the new mesh
            params: Creation parameters:
                - primitive: Type of primitive (cube, sphere, plane, etc.)
                - size: Size for primitives
                - vertices: List of vertex coordinates
                - edges: List of edge indices
                - faces: List of face vertex indices
                
        Returns:
            Dict with created mesh info
        """
        import bpy  # type: ignore
        
        mesh = bpy.data.meshes.new(name=name)
        
        primitive = params.get("primitive")
        if primitive:
            import bmesh  # type: ignore
            bm = bmesh.new()
            
            size = params.get("size", 2.0)
            
            if primitive.lower() == "cube":
                bmesh.ops.create_cube(bm, size=size)
            elif primitive.lower() == "sphere":
                segments = params.get("segments", 32)
                ring_count = params.get("ring_count", 16)
                bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=ring_count, radius=size/2)
            elif primitive.lower() == "cylinder":
                segments = params.get("segments", 32)
                depth = params.get("depth", 2.0)
                bmesh.ops.create_cone(bm, segments=segments, radius1=size/2, radius2=size/2, depth=depth)
            elif primitive.lower() == "cone":
                segments = params.get("segments", 32)
                depth = params.get("depth", 2.0)
                bmesh.ops.create_cone(bm, segments=segments, radius1=size/2, radius2=0, depth=depth)
            elif primitive.lower() == "plane":
                bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size)
            elif primitive.lower() == "icosphere":
                subdivisions = params.get("subdivisions", 2)
                bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=size/2)
            elif primitive.lower() == "torus":
                major_radius = params.get("major_radius", 1.0)
                minor_radius = params.get("minor_radius", 0.25)
                major_segments = params.get("major_segments", 48)
                minor_segments = params.get("minor_segments", 12)
                bmesh.ops.create_torus(
                    bm,
                    major_segments=major_segments,
                    minor_segments=minor_segments,
                    major_radius=major_radius,
                    minor_radius=minor_radius,
                )
            
            bm.to_mesh(mesh)
            bm.free()
        
        vertices = params.get("vertices")
        edges = params.get("edges")
        faces = params.get("faces")
        
        if vertices is not None:
            mesh.from_pydata(
                vertices,
                edges if edges else [],
                faces if faces else []
            )
            mesh.update()
        
        return {
            "name": mesh.name,
            "type": "mesh",
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
        }
    
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
        
        if obj_eval is not None:
            obj_eval.to_mesh_clear()
        
        return result
    
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
            items.append({
                "name": mesh.name,
                "vertices": len(mesh.vertices),
                "polygons": len(mesh.polygons),
                "users": mesh.users,
            })
        
        return {"items": items, "count": len(items)}
