# -*- coding: utf-8 -*-
"""Mask handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class MaskHandler(GenericCollectionHandler):
    """Handler for Blender mask data type (bpy.data.masks)."""

    data_type = DataType.MASK

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new mask."""
        import bpy  # type: ignore

        mask = bpy.data.masks.new(name=name)
        return {"name": mask.name}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {
            "name": item.name,
            "layers_count": len(item.layers),
        }

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "layers_count": len(item.layers)}
