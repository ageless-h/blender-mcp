# -*- coding: utf-8 -*-
"""Palette handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class PaletteHandler(BaseHandler):
    """Handler for Blender palette data type (bpy.data.palettes)."""

    data_type = DataType.PALETTE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new palette.

        Args:
            name: Name for new palette
            params: Creation parameters:
                - colors: List of color values (r, g, b, a)

        Returns:
            Dict with created palette info
        """
        import bpy  # type: ignore

        palette = bpy.data.palettes.new(name=name)

        colors = params.get("colors", [])
        for color_data in colors:
            color = palette.colors.new()
            if isinstance(color_data, (list, tuple)):
                color.color = color_data[:3]
            elif isinstance(color_data, dict):
                if "color" in color_data:
                    color.color = color_data["color"][:3]

        return {"name": palette.name, "colors": len(palette.colors)}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read palette properties.

        Args:
            name: Name of palette
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with palette properties
        """
        import bpy  # type: ignore

        palette = bpy.data.palettes.get(name)
        if palette is None:
            raise KeyError(f"Palette '{name}' not found")

        if path:
            value = self._get_nested_attr(palette, path)
            return {"name": name, "path": path, "value": value}

        result = {
            "name": palette.name,
            "colors_count": len(palette.colors),
        }

        if params.get("include_colors"):
            result["colors"] = [
                {"name": c.name, "color": list(c.color)} for c in palette.colors
            ]

        return result

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a palette.

        Args:
            name: Name of palette
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        palette = bpy.data.palettes.get(name)
        if palette is None:
            raise KeyError(f"Palette '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(palette, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a palette.

        Args:
            name: Name of palette to delete
            params: Deletion parameters

        Returns:
            Dict with deleted palette name
        """
        import bpy  # type: ignore

        palette = bpy.data.palettes.get(name)
        if palette is None:
            raise KeyError(f"Palette '{name}' not found")

        bpy.data.palettes.remove(palette)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all palettes.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [
            {"name": p.name, "colors_count": len(p.colors)} for p in bpy.data.palettes
        ]
        return {"items": items, "count": len(items)}
