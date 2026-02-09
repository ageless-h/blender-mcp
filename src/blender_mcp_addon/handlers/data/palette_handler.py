# -*- coding: utf-8 -*-
"""Palette handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class PaletteHandler(GenericCollectionHandler):
    """Handler for Blender palette data type (bpy.data.palettes)."""

    data_type = DataType.PALETTE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new palette."""
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

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "colors_count": len(item.colors)}

    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read palette properties, with optional include_colors expansion."""
        item = self.get_item(name)
        if item is None:
            raise KeyError(f"{self._type_label()} '{name}' not found")

        if path:
            value = self._get_nested_attr(item, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            return {"name": name, "path": path, "value": value}

        result = self._read_summary(item)
        if params.get("include_colors"):
            result["colors"] = [
                {"name": c.name, "color": list(c.color)} for c in item.colors
            ]
        return result

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "colors_count": len(item.colors)}
