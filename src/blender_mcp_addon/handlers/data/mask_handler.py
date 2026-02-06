# -*- coding: utf-8 -*-
"""Mask handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class MaskHandler(BaseHandler):
    """Handler for Blender mask data type (bpy.data.masks)."""

    data_type = DataType.MASK

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new mask.

        Args:
            name: Name for new mask
            params: Creation parameters

        Returns:
            Dict with created mask info
        """
        import bpy  # type: ignore

        mask = bpy.data.masks.new(name=name)
        return {"name": mask.name}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read mask properties.

        Args:
            name: Name of mask
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with mask properties
        """
        import bpy  # type: ignore

        mask = bpy.data.masks.get(name)
        if mask is None:
            raise KeyError(f"Mask '{name}' not found")

        if path:
            value = self._get_nested_attr(mask, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": mask.name,
            "layers_count": len(mask.layers),
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a mask.

        Args:
            name: Name of mask
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        mask = bpy.data.masks.get(name)
        if mask is None:
            raise KeyError(f"Mask '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(mask, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a mask.

        Args:
            name: Name of mask to delete
            params: Deletion parameters

        Returns:
            Dict with deleted mask name
        """
        import bpy  # type: ignore

        mask = bpy.data.masks.get(name)
        if mask is None:
            raise KeyError(f"Mask '{name}' not found")

        bpy.data.masks.remove(mask)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all masks.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [
            {"name": m.name, "layers_count": len(m.layers)} for m in bpy.data.masks
        ]
        return {"items": items, "count": len(items)}
