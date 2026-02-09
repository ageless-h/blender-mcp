# -*- coding: utf-8 -*-
"""Lattice handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class LatticeHandler(GenericCollectionHandler):
    """Handler for Blender lattice data type (bpy.data.lattices)."""

    data_type = DataType.LATTICE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new lattice."""
        import bpy  # type: ignore

        points_u = params.get("points_u", 2)
        points_v = params.get("points_v", 2)
        points_w = params.get("points_w", 2)

        lattice = bpy.data.lattices.new(name=name)
        lattice.points_u = points_u
        lattice.points_v = points_v
        lattice.points_w = points_w

        return {
            "name": lattice.name,
            "points_u": points_u,
            "points_v": points_v,
            "points_w": points_w,
        }

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {
            "name": item.name,
            "points_u": item.points_u,
            "points_v": item.points_v,
            "points_w": item.points_w,
            "points_total": len(item.points),
        }

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {
            "name": item.name,
            "points_u": item.points_u,
            "points_v": item.points_v,
            "points_w": item.points_w,
        }
