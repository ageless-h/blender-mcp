# -*- coding: utf-8 -*-
"""Sound handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class SoundHandler(GenericCollectionHandler):
    """Handler for Blender sound data type (bpy.data.sounds)."""

    data_type = DataType.SOUND

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new sound."""
        import bpy  # type: ignore

        sound = bpy.data.sounds.new(name=name)
        filepath = params.get("filepath")
        if filepath:
            sound.filepath = filepath
        return {"name": sound.name}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": item.filepath}

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": item.filepath}
