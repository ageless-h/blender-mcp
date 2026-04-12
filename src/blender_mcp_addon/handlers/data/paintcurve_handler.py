# -*- coding: utf-8 -*-
"""Paint curve handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class PaintCurveHandler(GenericCollectionHandler):
    """Handler for Blender paint curve data type (bpy.data.paint_curves)."""

    data_type = DataType.PAINTCURVE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new paint curve."""
        import bpy  # type: ignore

        paint_curve = bpy.data.paint_curves.new(name=name)
        return {"name": paint_curve.name}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "points_count": len(item.points)}

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "points_count": len(item.points)}

    def _type_label(self) -> str:
        return "Paint curve"
