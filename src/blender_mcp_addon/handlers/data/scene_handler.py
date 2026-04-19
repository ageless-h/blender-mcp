# -*- coding: utf-8 -*-
"""Scene handler for unified CRUD operations."""
from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class SceneHandler(GenericCollectionHandler):
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

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {
            "name": item.name,
            "objects": len(item.objects),
            "frame_start": item.frame_start,
            "frame_end": item.frame_end,
            "frame_current": item.frame_current,
            "render_engine": item.render.engine,
            "resolution_x": item.render.resolution_x,
            "resolution_y": item.render.resolution_y,
            "fps": item.render.fps,
            "world": item.world.name if item.world else None,
            "camera": item.camera.name if item.camera else None,
        }

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {
            "name": item.name,
            "frame_range": [item.frame_start, item.frame_end],
        }

    def _custom_write(self, item: Any, prop_path: str, value: Any) -> bool:
        if prop_path == "camera":
            import bpy  # type: ignore
            camera_obj = bpy.data.objects.get(value) if value else None
            item.camera = camera_obj
            return True
        elif prop_path == "world":
            import bpy  # type: ignore
            world = bpy.data.worlds.get(value) if value else None
            item.world = world
            return True
        return False

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
