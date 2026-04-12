# -*- coding: utf-8 -*-
"""New curves handler for unified CRUD operations (Blender 5.0+)."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class CurvesNewHandler(BaseHandler):
    """Handler for Blender new curves data type (bpy.data.curves - Blender 5.0+ system)."""

    data_type = DataType.CURVES_NEW

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new curves object (Blender 5.0+).

        Args:
            name: Name for new curves
            params: Creation parameters

        Returns:
            Dict with created curves info
        """
        import bpy  # type: ignore

        curves = bpy.data.curves.new(name=name)
        return {"name": curves.name}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read curves properties.

        Args:
            name: Name of curves
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with curves properties
        """
        import bpy  # type: ignore

        curves = bpy.data.curves.get(name)
        if curves is None:
            raise KeyError(f"Curves '{name}' not found")

        if path:
            value = self._get_nested_attr(curves, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": curves.name,
            "resolution_u": curves.resolution_u,
            "resolution_v": curves.resolution_v,
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to curves.

        Args:
            name: Name of curves
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        curves = bpy.data.curves.get(name)
        if curves is None:
            raise KeyError(f"Curves '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(curves, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete curves.

        Args:
            name: Name of curves to delete
            params: Deletion parameters

        Returns:
            Dict with deleted curves name
        """
        import bpy  # type: ignore

        curves = bpy.data.curves.get(name)
        if curves is None:
            raise KeyError(f"Curves '{name}' not found")

        bpy.data.curves.remove(curves)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all curves.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [
            {"name": c.name, "resolution_u": c.resolution_u} for c in bpy.data.curves
        ]
        return {"items": items, "count": len(items)}
