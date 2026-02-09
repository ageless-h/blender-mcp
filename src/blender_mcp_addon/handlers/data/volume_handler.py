# -*- coding: utf-8 -*-
"""Volume handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class VolumeHandler(GenericCollectionHandler):
    """Handler for Blender volume data type (bpy.data.volumes)."""

    data_type = DataType.VOLUME

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new volume."""
        import bpy  # type: ignore

        volume = bpy.data.volumes.new(name=name)
        filepath = params.get("filepath")
        if filepath:
            volume.filepath = filepath
        return {"name": volume.name}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": item.filepath}

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": item.filepath}
