# -*- coding: utf-8 -*-
"""Scene handler for unified CRUD operations."""
from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class SceneHandler(BaseHandler):
    """Handler for Blender scene data type (bpy.data.scenes)."""
    
    data_type = DataType.SCENE
    
    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new scene.
        
        Args:
            name: Name for the new scene
            params: Creation parameters
            
        Returns:
            Dict with created scene info
        """
        import bpy  # type: ignore
        
        scene = bpy.data.scenes.new(name=name)
        
        return {
            "name": scene.name,
            "type": "scene",
        }
    
    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read scene properties.
        
        Args:
            name: Name of the scene
            path: Optional property path
            params: Read parameters
            
        Returns:
            Dict with scene properties
        """
        import bpy  # type: ignore
        
        scene = bpy.data.scenes.get(name)
        if scene is None:
            raise KeyError(f"Scene '{name}' not found")
        
        if path:
            value = self._get_nested_attr(scene, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            return {"name": name, "path": path, "value": value}
        
        return {
            "name": scene.name,
            "objects_count": len(scene.objects),
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "frame_current": scene.frame_current,
            "render_engine": scene.render.engine,
            "resolution_x": scene.render.resolution_x,
            "resolution_y": scene.render.resolution_y,
            "fps": scene.render.fps,
            "world": scene.world.name if scene.world else None,
            "camera": scene.camera.name if scene.camera else None,
        }
    
    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write properties to a scene.
        
        Args:
            name: Name of the scene
            properties: Dict of property paths to values
            params: Write parameters
            
        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore
        
        scene = bpy.data.scenes.get(name)
        if scene is None:
            raise KeyError(f"Scene '{name}' not found")
        
        modified = []
        for prop_path, value in properties.items():
            if prop_path == "camera":
                camera_obj = bpy.data.objects.get(value) if value else None
                scene.camera = camera_obj
            elif prop_path == "world":
                world = bpy.data.worlds.get(value) if value else None
                scene.world = world
            else:
                self._set_nested_attr(scene, prop_path, value)
            modified.append(prop_path)
        
        return {"name": name, "modified": modified}
    
    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a scene.
        
        Args:
            name: Name of the scene to delete
            params: Deletion parameters
            
        Returns:
            Dict with deleted scene name
        """
        import bpy  # type: ignore
        
        scene = bpy.data.scenes.get(name)
        if scene is None:
            raise KeyError(f"Scene '{name}' not found")
        
        if len(bpy.data.scenes) <= 1:
            raise ValueError("Cannot delete the only scene")
        
        bpy.data.scenes.remove(scene)
        return {"deleted": name}
    
    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all scenes.
        
        Args:
            filter_params: Optional filter criteria
            
        Returns:
            Dict with items list
        """
        import bpy  # type: ignore
        
        items = []
        for scene in bpy.data.scenes:
            items.append({
                "name": scene.name,
                "objects_count": len(scene.objects),
                "frame_range": [scene.frame_start, scene.frame_end],
            })
        
        return {"items": items, "count": len(items)}
