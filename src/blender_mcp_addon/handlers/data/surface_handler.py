# -*- coding: utf-8 -*-
"""Surface handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class SurfaceHandler(BaseHandler):
    """Handler for Blender surface data type (bpy.data.surfaces)."""

    data_type = DataType.SURFACE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new surface.

        Args:
            name: Name for new surface
            params: Creation parameters

        Returns:
            Dict with created surface info
        """
        import bpy  # type: ignore

        surface = bpy.data.surfaces.new(name=name)

        return {"name": surface.name}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read surface properties.

        Args:
            name: Name of surface
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with surface properties
        """
        import bpy  # type: ignore

        surface = bpy.data.surfaces.get(name)
        if surface is None:
            raise KeyError(f"Surface '{name}' not found")

        if path:
            value = self._get_nested_attr(surface, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": surface.name,
            "splines_count": len(surface.splines),
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a surface.

        Args:
            name: Name of surface
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        surface = bpy.data.surfaces.get(name)
        if surface is None:
            raise KeyError(f"Surface '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(surface, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a surface.

        Args:
            name: Name of surface to delete
            params: Deletion parameters

        Returns:
            Dict with deleted surface name
        """
        import bpy  # type: ignore

        surface = bpy.data.surfaces.get(name)
        if surface is None:
            raise KeyError(f"Surface '{name}' not found")

        bpy.data.surfaces.remove(surface)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all surfaces.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [
            {"name": s.name, "splines_count": len(s.splines)} for s in bpy.data.surfaces
        ]
        return {"items": items, "count": len(items)}
