# -*- coding: utf-8 -*-
"""Paint curve handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class PaintCurveHandler(BaseHandler):
    """Handler for Blender paint curve data type (bpy.data.paint_curves)."""

    data_type = DataType.PAINTCURVE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new paint curve.

        Args:
            name: Name for new paint curve
            params: Creation parameters

        Returns:
            Dict with created paint curve info
        """
        import bpy  # type: ignore

        paint_curve = bpy.data.paint_curves.new(name=name)
        return {"name": paint_curve.name}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read paint curve properties.

        Args:
            name: Name of paint curve
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with paint curve properties
        """
        import bpy  # type: ignore

        paint_curve = bpy.data.paint_curves.get(name)
        if paint_curve is None:
            raise KeyError(f"Paint curve '{name}' not found")

        if path:
            value = self._get_nested_attr(paint_curve, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": paint_curve.name,
            "points_count": len(paint_curve.points),
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a paint curve.

        Args:
            name: Name of paint curve
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        paint_curve = bpy.data.paint_curves.get(name)
        if paint_curve is None:
            raise KeyError(f"Paint curve '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(paint_curve, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a paint curve.

        Args:
            name: Name of paint curve to delete
            params: Deletion parameters

        Returns:
            Dict with deleted paint curve name
        """
        import bpy  # type: ignore

        paint_curve = bpy.data.paint_curves.get(name)
        if paint_curve is None:
            raise KeyError(f"Paint curve '{name}' not found")

        bpy.data.paint_curves.remove(paint_curve)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all paint curves.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [
            {"name": p.name, "points_count": len(p.points)}
            for p in bpy.data.paint_curves
        ]
        return {"items": items, "count": len(items)}
