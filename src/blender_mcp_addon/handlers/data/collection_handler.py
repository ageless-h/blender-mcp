# -*- coding: utf-8 -*-
"""Collection handler for unified CRUD operations."""
from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class CollectionHandler(BaseHandler):
    """Handler for Blender collection data type (bpy.data.collections)."""
    
    data_type = DataType.COLLECTION
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new collection.
        
        Args:
            name: Name for the new collection
            params: Creation parameters:
                - parent: Parent collection name (links to scene collection if not specified)
                - color_tag: Color tag for the collection
                
        Returns:
            Dict with created collection info
        """
        import bpy  # type: ignore
        
        collection = bpy.data.collections.new(name=name)
        
        parent_name = params.get("parent")
        if parent_name:
            parent = bpy.data.collections.get(parent_name)
            if parent:
                parent.children.link(collection)
            else:
                bpy.context.scene.collection.children.link(collection)
        else:
            bpy.context.scene.collection.children.link(collection)
        
        color_tag = params.get("color_tag")
        if color_tag:
            collection.color_tag = color_tag
        
        return {
            "name": collection.name,
            "type": "collection",
        }
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read collection properties.
        
        Args:
            name: Name of the collection
            path: Optional property path
            params: Read parameters
            
        Returns:
            Dict with collection properties
        """
        import bpy  # type: ignore
        
        collection = bpy.data.collections.get(name)
        if collection is None:
            raise KeyError(f"Collection '{name}' not found")
        
        if path:
            value = self._get_nested_attr(collection, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            return {"name": name, "path": path, "value": value}
        
        return {
            "name": collection.name,
            "objects": [obj.name for obj in collection.objects],
            "children": [child.name for child in collection.children],
            "hide_viewport": collection.hide_viewport,
            "hide_render": collection.hide_render,
            "color_tag": collection.color_tag,
        }
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write properties to a collection.
        
        Args:
            name: Name of the collection
            properties: Dict of property paths to values
            params: Write parameters
            
        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore
        
        collection = bpy.data.collections.get(name)
        if collection is None:
            raise KeyError(f"Collection '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(collection, prop_path, value)
            modified.append(prop_path)
        
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a collection.
        
        Args:
            name: Name of the collection to delete
            params: Deletion parameters
            
        Returns:
            Dict with deleted collection name
        """
        import bpy  # type: ignore
        
        collection = bpy.data.collections.get(name)
        if collection is None:
            raise KeyError(f"Collection '{name}' not found")
        
        bpy.data.collections.remove(collection)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all collections.
        
        Args:
            filter_params: Optional filter criteria
            
        Returns:
            Dict with items list
        """
        import bpy  # type: ignore
        
        items = []
        for collection in bpy.data.collections:
            items.append({
                "name": collection.name,
                "objects_count": len(collection.objects),
                "children_count": len(collection.children),
            })
        
        return {"items": items, "count": len(items)}
