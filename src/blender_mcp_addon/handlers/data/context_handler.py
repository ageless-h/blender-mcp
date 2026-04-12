# -*- coding: utf-8 -*-
"""Context handler for pseudo-type access to bpy.context."""
from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class ContextHandler(BaseHandler):
    """Handler for context pseudo-type (bpy.context access)."""

    data_type = DataType.CONTEXT

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Context cannot be created."""
        raise NotImplementedError("Context is a pseudo-type and cannot be created")

    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read context state.

        Args:
            name: Ignored for context
            path: Optional property path to read specific property
            params: Read parameters

        Returns:
            Dict with context state
        """
        import bpy  # type: ignore

        ctx = bpy.context

        if path:
            value = self._get_nested_attr(ctx, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            elif hasattr(value, "name") and not isinstance(value, str):
                value = getattr(value, "name", value)
            return {"path": path, "value": value}

        active_obj = ctx.active_object
        selected = getattr(ctx, "selected_objects", []) or []

        return {
            "mode": ctx.mode,
            "active_object": active_obj.name if active_obj else None,
            "selected_objects": [obj.name for obj in selected],
            "scene": ctx.scene.name if ctx.scene else None,
            "view_layer": ctx.view_layer.name if ctx.view_layer else None,
            "workspace": ctx.workspace.name if ctx.workspace else None,
            "area_type": ctx.area.type if ctx.area else None,
            "region_type": ctx.region.type if ctx.region else None,
            "tool": ctx.tool_settings.workspace_tool_type if hasattr(ctx.tool_settings, "workspace_tool_type") else None,
        }

    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write context state (selection, active object, mode).

        Args:
            name: Ignored for context
            properties: Dict of property paths to values:
                - mode: Switch to mode (OBJECT, EDIT, SCULPT, etc.)
                - active_object: Set active object by name
                - selected_objects: List of object names to select
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        modified = []

        if "selected_objects" in properties:
            bpy.ops.object.select_all(action='DESELECT')
            for obj_name in properties["selected_objects"]:
                obj = bpy.data.objects.get(obj_name)
                if obj:
                    obj.select_set(True)
            modified.append("selected_objects")

        if "active_object" in properties:
            obj_name = properties["active_object"]
            obj = bpy.data.objects.get(obj_name) if obj_name else None
            bpy.context.view_layer.objects.active = obj
            modified.append("active_object")

        if "mode" in properties:
            target_mode = properties["mode"].upper()
            current_mode = bpy.context.mode

            if target_mode != current_mode:
                if target_mode == "OBJECT":
                    bpy.ops.object.mode_set(mode='OBJECT')
                elif target_mode == "EDIT" or target_mode == "EDIT_MESH":
                    bpy.ops.object.mode_set(mode='EDIT')
                elif target_mode == "SCULPT":
                    bpy.ops.object.mode_set(mode='SCULPT')
                elif target_mode == "VERTEX_PAINT":
                    bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                elif target_mode == "WEIGHT_PAINT":
                    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
                elif target_mode == "TEXTURE_PAINT":
                    bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
                elif target_mode == "POSE":
                    bpy.ops.object.mode_set(mode='POSE')
                modified.append("mode")

        if "scene" in properties:
            scene = bpy.data.scenes.get(properties["scene"])
            if scene:
                bpy.context.window.scene = scene
                modified.append("scene")

        return {"modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Context cannot be deleted."""
        raise NotImplementedError("Context is a pseudo-type and cannot be deleted")

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List available context attributes."""
        return {
            "items": [
                {"name": "mode", "description": "Current editing mode"},
                {"name": "active_object", "description": "Currently active object"},
                {"name": "selected_objects", "description": "List of selected objects"},
                {"name": "scene", "description": "Current scene"},
                {"name": "view_layer", "description": "Current view layer"},
                {"name": "workspace", "description": "Current workspace"},
            ],
            "count": 6,
        }
