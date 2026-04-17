# -*- coding: utf-8 -*-
"""Sound handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class SoundHandler(GenericCollectionHandler):
    """Handler for Blender sound data type (bpy.data.sounds)."""

    data_type = DataType.SOUND

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new sound."""
        import bpy  # type: ignore

        filepath = params.get("filepath")
        if not filepath:
            raise ValueError("'filepath' parameter is required for sound creation")
        sound = bpy.data.sounds.load(filepath)
        if name and name != sound.name:
            sound.name = name
        return {"name": sound.name}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": item.filepath}

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": item.filepath}
