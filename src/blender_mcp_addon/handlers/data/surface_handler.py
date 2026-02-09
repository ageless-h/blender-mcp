# -*- coding: utf-8 -*-
"""Surface handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class SurfaceHandler(GenericCollectionHandler):
    """Handler for Blender surface data type (bpy.data.surfaces)."""

    data_type = DataType.SURFACE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new surface."""
        import bpy  # type: ignore

        surface = bpy.data.surfaces.new(name=name)
        return {"name": surface.name}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {
            "name": item.name,
            "splines_count": len(item.splines),
        }

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "splines_count": len(item.splines)}
