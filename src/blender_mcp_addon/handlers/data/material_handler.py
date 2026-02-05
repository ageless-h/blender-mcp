# -*- coding: utf-8 -*-
"""Material handler for unified CRUD operations."""
from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class MaterialHandler(BaseHandler):
    """Handler for Blender material data type (bpy.data.materials)."""
    
    data_type = DataType.MATERIAL
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new material.
        
        Args:
            name: Name for the new material
            params: Creation parameters:
                - use_nodes: Enable node-based material (default: True)
                - color: Base color as [r, g, b, a]
                
        Returns:
            Dict with created material info
        """
        import bpy  # type: ignore
        
        mat = bpy.data.materials.new(name=name)
        
        use_nodes = params.get("use_nodes", True)
        if use_nodes:
            mat.use_nodes = True
        
        color = params.get("color")
        if color and mat.use_nodes:
            principled = mat.node_tree.nodes.get("Principled BSDF")
            if principled:
                principled.inputs["Base Color"].default_value = tuple(color)
        
        return {
            "name": mat.name,
            "type": "material",
            "use_nodes": mat.use_nodes,
        }
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read material properties.
        
        Args:
            name: Name of the material
            path: Optional property path
            params: Read parameters
            
        Returns:
            Dict with material properties
        """
        import bpy  # type: ignore
        
        mat = bpy.data.materials.get(name)
        if mat is None:
            raise KeyError(f"Material '{name}' not found")
        
        if path:
            value = self._get_nested_attr(mat, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            return {"name": name, "path": path, "value": value}
        
        result = {
            "name": mat.name,
            "use_nodes": mat.use_nodes,
            "blend_method": mat.blend_method,
            "shadow_method": mat.shadow_method,
            "users": mat.users,
        }
        
        if mat.use_nodes and mat.node_tree:
            principled = mat.node_tree.nodes.get("Principled BSDF")
            if principled:
                result["base_color"] = list(principled.inputs["Base Color"].default_value)
                result["metallic"] = principled.inputs["Metallic"].default_value
                result["roughness"] = principled.inputs["Roughness"].default_value
            
            result["nodes"] = [
                {"name": n.name, "type": n.type, "label": n.label}
                for n in mat.node_tree.nodes
            ]
        
        return result
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write properties to a material.
        
        Args:
            name: Name of the material
            properties: Dict of property paths to values
            params: Write parameters
            
        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore
        
        mat = bpy.data.materials.get(name)
        if mat is None:
            raise KeyError(f"Material '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            if prop_path == "base_color" and mat.use_nodes:
                principled = mat.node_tree.nodes.get("Principled BSDF")
                if principled:
                    principled.inputs["Base Color"].default_value = tuple(value)
                    modified.append("base_color")
            elif prop_path == "metallic" and mat.use_nodes:
                principled = mat.node_tree.nodes.get("Principled BSDF")
                if principled:
                    principled.inputs["Metallic"].default_value = value
                    modified.append("metallic")
            elif prop_path == "roughness" and mat.use_nodes:
                principled = mat.node_tree.nodes.get("Principled BSDF")
                if principled:
                    principled.inputs["Roughness"].default_value = value
                    modified.append("roughness")
            else:
                self._set_nested_attr(mat, prop_path, value)
                modified.append(prop_path)
        
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a material.
        
        Args:
            name: Name of the material to delete
            params: Deletion parameters
            
        Returns:
            Dict with deleted material name
        """
        import bpy  # type: ignore
        
        mat = bpy.data.materials.get(name)
        if mat is None:
            raise KeyError(f"Material '{name}' not found")
        
        bpy.data.materials.remove(mat)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all materials.
        
        Args:
            filter_params: Optional filter criteria
            
        Returns:
            Dict with items list
        """
        import bpy  # type: ignore
        
        items = []
        for mat in bpy.data.materials:
            items.append({
                "name": mat.name,
                "use_nodes": mat.use_nodes,
                "users": mat.users,
            })
        
        return {"items": items, "count": len(items)}
    
    def link(
        self,
        source_name: str,
        target_type: DataType,
        target_name: str,
        unlink: bool = False,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Link or unlink material to/from an object.
        
        Args:
            source_name: Name of the material
            target_type: Must be OBJECT
            target_name: Name of the object
            unlink: If True, unlink instead of link
            params: Additional parameters:
                - slot: Material slot index (default: 0)
                
        Returns:
            Dict with action result
        """
        import bpy  # type: ignore
        
        if target_type != DataType.OBJECT:
            return {"error": f"Materials can only be linked to objects, not {target_type.value}"}
        
        mat = bpy.data.materials.get(source_name)
        if mat is None:
            raise KeyError(f"Material '{source_name}' not found")
        
        obj = bpy.data.objects.get(target_name)
        if obj is None:
            raise KeyError(f"Object '{target_name}' not found")
        
        params = params or {}
        slot = params.get("slot", 0)
        
        if unlink:
            if slot < len(obj.material_slots):
                obj.material_slots[slot].material = None
                return {"action": "unlink", "material": source_name, "object": target_name, "slot": slot}
            return {"action": "unlink", "skipped": True, "reason": "Slot index out of range"}
        else:
            while len(obj.material_slots) <= slot:
                obj.data.materials.append(None)
            obj.material_slots[slot].material = mat
            return {"action": "link", "material": source_name, "object": target_name, "slot": slot}
