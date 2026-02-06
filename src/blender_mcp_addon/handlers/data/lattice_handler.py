# -*- coding: utf-8 -*-
"""Lattice handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class LatticeHandler(BaseHandler):
    """Handler for Blender lattice data type (bpy.data.lattices)."""

    data_type = DataType.LATTICE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new lattice.

        Args:
            name: Name for new lattice
            params: Creation parameters:
                - points_u: U dimension point count
                - points_v: V dimension point count
                - points_w: W dimension point count

        Returns:
            Dict with created lattice info
        """
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

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read lattice properties.

        Args:
            name: Name of lattice
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with lattice properties
        """
        import bpy  # type: ignore

        lattice = bpy.data.lattices.get(name)
        if lattice is None:
            raise KeyError(f"Lattice '{name}' not found")

        if path:
            value = self._get_nested_attr(lattice, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": lattice.name,
            "points_u": lattice.points_u,
            "points_v": lattice.points_v,
            "points_w": lattice.points_w,
            "points_total": len(lattice.points),
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a lattice.

        Args:
            name: Name of lattice
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        lattice = bpy.data.lattices.get(name)
        if lattice is None:
            raise KeyError(f"Lattice '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(lattice, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a lattice.

        Args:
            name: Name of lattice to delete
            params: Deletion parameters

        Returns:
            Dict with deleted lattice name
        """
        import bpy  # type: ignore

        lattice = bpy.data.lattices.get(name)
        if lattice is None:
            raise KeyError(f"Lattice '{name}' not found")

        bpy.data.lattices.remove(lattice)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all lattices.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [
            {
                "name": l.name,
                "points_u": l.points_u,
                "points_v": l.points_v,
                "points_w": l.points_w,
            }
            for l in bpy.data.lattices
        ]
        return {"items": items, "count": len(items)}
