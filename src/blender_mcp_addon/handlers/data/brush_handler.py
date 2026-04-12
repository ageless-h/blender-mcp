# -*- coding: utf-8 -*-
"""Brush handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class BrushHandler(GenericCollectionHandler):
    """Handler for Blender brush data type (bpy.data.brushes)."""

    data_type = DataType.BRUSH

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new brush."""
        import bpy  # type: ignore

        mode = params.get("mode", "SCULPT")
        brush = bpy.data.brushes.new(name=name, mode=mode)
        return {"name": brush.name, "mode": brush.mode}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": item.name,
            "mode": item.mode,
        }
        if item.mode == "SCULPT":
            result["size"] = item.size
            result["strength"] = item.strength
        elif item.mode == "PAINT":
            result["size"] = item.size
            result["color"] = list(item.color) if hasattr(item, "color") else None
        return result

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "mode": item.mode}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List brushes, with optional mode filter."""
        filter_params = filter_params or {}
        mode = filter_params.get("mode")

        collection = self.get_collection()
        if collection is None:
            return {"items": [], "count": 0}

        items = []
        for brush in collection:
            if mode and brush.mode != mode.upper():
                continue
            items.append(self._list_fields(brush))
        return {"items": items, "count": len(items)}
