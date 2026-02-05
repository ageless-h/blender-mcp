# -*- coding: utf-8 -*-
"""Modifier handler for attached type access."""
from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class ModifierHandler(BaseHandler):
    """Handler for modifier attached type (object.modifiers access)."""
    
    data_type = DataType.MODIFIER
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new modifier on an object.
        
        Args:
            name: Name for the new modifier
            params: Creation parameters:
                - object: Name of the parent object (required)
                - type: Modifier type (SUBSURF, ARRAY, MIRROR, etc.)
                
        Returns:
            Dict with created modifier info
        """
        import bpy  # type: ignore
        
        object_name = params.get("object")
        if not object_name:
            raise ValueError("'object' parameter is required for modifier creation")
        
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")
        
        modifier_type = params.get("type", "SUBSURF")
        modifier = obj.modifiers.new(name=name, type=modifier_type)
        
        settings = params.get("settings", {})
        for key, value in settings.items():
            if hasattr(modifier, key):
                setattr(modifier, key, value)
        
        return {
            "name": modifier.name,
            "type": modifier.type,
            "object": object_name,
        }
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read modifier properties.
        
        Args:
            name: Name of the modifier
            path: Optional property path
            params: Read parameters:
                - object: Name of the parent object (required)
                
        Returns:
            Dict with modifier properties
        """
        import bpy  # type: ignore
        
        object_name = params.get("object")
        if not object_name:
            raise ValueError("'object' parameter is required for modifier read")
        
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")
        
        modifier = obj.modifiers.get(name)
        if modifier is None:
            raise KeyError(f"Modifier '{name}' not found on object '{object_name}'")
        
        if path:
            value = self._get_nested_attr(modifier, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            return {"name": name, "object": object_name, "path": path, "value": value}
        
        result = {
            "name": modifier.name,
            "type": modifier.type,
            "object": object_name,
            "show_viewport": modifier.show_viewport,
            "show_render": modifier.show_render,
            "show_in_editmode": modifier.show_in_editmode,
        }
        
        if modifier.type == "SUBSURF":
            result["levels"] = modifier.levels
            result["render_levels"] = modifier.render_levels
        elif modifier.type == "ARRAY":
            result["count"] = modifier.count
            result["use_relative_offset"] = modifier.use_relative_offset
        elif modifier.type == "MIRROR":
            result["use_axis"] = [modifier.use_axis[0], modifier.use_axis[1], modifier.use_axis[2]]
        elif modifier.type == "BOOLEAN":
            result["operation"] = modifier.operation
            result["object"] = modifier.object.name if modifier.object else None
        elif modifier.type == "SOLIDIFY":
            result["thickness"] = modifier.thickness
            result["offset"] = modifier.offset
        elif modifier.type == "BEVEL":
            result["width"] = modifier.width
            result["segments"] = modifier.segments
        
        return result
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write properties to a modifier.
        
        Args:
            name: Name of the modifier
            properties: Dict of property paths to values
            params: Write parameters:
                - object: Name of the parent object (required)
                
        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore
        
        object_name = params.get("object")
        if not object_name:
            raise ValueError("'object' parameter is required for modifier write")
        
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")
        
        modifier = obj.modifiers.get(name)
        if modifier is None:
            raise KeyError(f"Modifier '{name}' not found on object '{object_name}'")
        
        modified = []
        for prop_path, value in properties.items():
            if hasattr(modifier, prop_path):
                setattr(modifier, prop_path, value)
                modified.append(prop_path)
            else:
                self._set_nested_attr(modifier, prop_path, value)
                modified.append(prop_path)
        
        return {"name": name, "object": object_name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a modifier from an object.
        
        Args:
            name: Name of the modifier to delete
            params: Deletion parameters:
                - object: Name of the parent object (required)
                
        Returns:
            Dict with deleted modifier name
        """
        import bpy  # type: ignore
        
        object_name = params.get("object")
        if not object_name:
            raise ValueError("'object' parameter is required for modifier delete")
        
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")
        
        modifier = obj.modifiers.get(name)
        if modifier is None:
            raise KeyError(f"Modifier '{name}' not found on object '{object_name}'")
        
        obj.modifiers.remove(modifier)
        return {"deleted": name, "object": object_name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all modifiers on an object.
        
        Args:
            filter_params: Filter criteria:
                - object: Name of the parent object (required)
                - type: Filter by modifier type
                
        Returns:
            Dict with items list
        """
        import bpy  # type: ignore
        
        filter_params = filter_params or {}
        object_name = filter_params.get("object")
        
        if not object_name:
            raise ValueError("'object' parameter is required for modifier list")
        
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")
        
        type_filter = filter_params.get("type")
        
        items = []
        for modifier in obj.modifiers:
            if type_filter and modifier.type != type_filter.upper():
                continue
            items.append({
                "name": modifier.name,
                "type": modifier.type,
                "show_viewport": modifier.show_viewport,
                "show_render": modifier.show_render,
            })
        
        return {"items": items, "count": len(items), "object": object_name}
