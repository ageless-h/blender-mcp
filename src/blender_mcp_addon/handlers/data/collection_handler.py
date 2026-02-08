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
            params: Read parameters:
                - max_depth: Maximum recursion depth for child collections (default: 10)
            
        Returns:
            Dict with collection tree
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
        
        max_depth = params.get("max_depth", 10)
        return self._read_collection_tree(collection, max_depth, 1)
    
    @staticmethod
    def _read_collection_tree(collection, max_depth: int, current_depth: int) -> dict[str, Any]:
        """Recursively read collection tree up to max_depth."""
        result: dict[str, Any] = {
            "name": collection.name,
            "objects": [obj.name for obj in collection.objects],
            "objects_count": len(collection.objects),
            "hide_viewport": collection.hide_viewport,
            "hide_render": collection.hide_render,
            "color_tag": collection.color_tag,
        }
        if current_depth < max_depth and collection.children:
            result["children"] = [
                CollectionHandler._read_collection_tree(child, max_depth, current_depth + 1)
                for child in collection.children
            ]
        else:
            result["children"] = [child.name for child in collection.children]
            result["children_count"] = len(collection.children)
        return result
    
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

    def link(
        self,
        source_name: str,
        target_type: DataType,
        target_name: str,
        unlink: bool = False,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Link/unlink collection to a parent collection or scene."""
        import bpy  # type: ignore
        
        collection = bpy.data.collections.get(source_name)
        if collection is None:
            raise KeyError(f"Collection '{source_name}' not found")
        
        params = params or {}
        
        if target_type == DataType.COLLECTION:
            parent = bpy.data.collections.get(target_name)
            if parent is None:
                raise KeyError(f"Collection '{target_name}' not found")
            if unlink:
                if collection.name in parent.children:
                    parent.children.unlink(collection)
                    return {"action": "unlink", "collection": source_name, "parent": target_name}
                return {"action": "unlink", "skipped": True, "reason": "Not linked"}
            if collection.name not in parent.children:
                parent.children.link(collection)
                return {"action": "link", "collection": source_name, "parent": target_name}
            return {"action": "link", "skipped": True, "reason": "Already linked"}
        
        if target_type == DataType.SCENE:
            scene_name = target_name or params.get("scene")
            scene = bpy.data.scenes.get(scene_name) if scene_name else bpy.context.scene
            if scene is None:
                raise KeyError(f"Scene '{scene_name}' not found")
            root = scene.collection
            if unlink:
                if collection.name in root.children:
                    root.children.unlink(collection)
                    return {"action": "unlink", "collection": source_name, "scene": scene.name}
                return {"action": "unlink", "skipped": True, "reason": "Not linked to scene"}
            if collection.name not in root.children:
                root.children.link(collection)
                return {"action": "link", "collection": source_name, "scene": scene.name}
            return {"action": "link", "skipped": True, "reason": "Already linked to scene"}
        
        return {"error": f"Collections can only be linked to collections or scenes, not {target_type.value}"}
