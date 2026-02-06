# -*- coding: utf-8 -*-
"""Brush handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class BrushHandler(BaseHandler):
    """Handler for Blender brush data type (bpy.data.brushes)."""

    data_type = DataType.BRUSH

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new brush.

        Args:
            name: Name for new brush
            params: Creation parameters:
                - mode: Brush mode (SCULPT, PAINT, VERTEX_PAINT, WEIGHT_PAINT, etc.)

        Returns:
            Dict with created brush info
        """
        import bpy  # type: ignore

        mode = params.get("mode", "SCULPT")
        brush = bpy.data.brushes.new(name=name, mode=mode)

        return {"name": brush.name, "mode": brush.mode}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read brush properties.

        Args:
            name: Name of brush
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with brush properties
        """
        import bpy  # type: ignore

        brush = bpy.data.brushes.get(name)
        if brush is None:
            raise KeyError(f"Brush '{name}' not found")

        if path:
            value = self._get_nested_attr(brush, path)
            return {"name": name, "path": path, "value": value}

        result = {
            "name": brush.name,
            "mode": brush.mode,
        }

        if brush.mode == "SCULPT":
            result["size"] = brush.size
            result["strength"] = brush.strength
        elif brush.mode == "PAINT":
            result["size"] = brush.size
            result["color"] = list(brush.color) if hasattr(brush, "color") else None

        return result

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a brush.

        Args:
            name: Name of brush
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        brush = bpy.data.brushes.get(name)
        if brush is None:
            raise KeyError(f"Brush '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(brush, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a brush.

        Args:
            name: Name of brush to delete
            params: Deletion parameters

        Returns:
            Dict with deleted brush name
        """
        import bpy  # type: ignore

        brush = bpy.data.brushes.get(name)
        if brush is None:
            raise KeyError(f"Brush '{name}' not found")

        bpy.data.brushes.remove(brush)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all brushes.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        filter_params = filter_params or {}
        mode = filter_params.get("mode")

        items = []
        for brush in bpy.data.brushes:
            if mode and brush.mode != mode.upper():
                continue
            items.append(
                {
                    "name": brush.name,
                    "mode": brush.mode,
                }
            )
        return {"items": items, "count": len(items)}
