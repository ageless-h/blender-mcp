# -*- coding: utf-8 -*-
"""Speaker handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class SpeakerHandler(GenericCollectionHandler):
    """Handler for Blender speaker data type (bpy.data.speakers)."""

    data_type = DataType.SPEAKER

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new speaker."""
        import bpy  # type: ignore

        speaker = bpy.data.speakers.new(name=name)
        if "volume" in params:
            speaker.volume = params["volume"]
        return {"name": speaker.name, "volume": speaker.volume}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": item.name,
            "volume": item.volume,
        }
        if item.sound:
            result["sound"] = item.sound.name
        return result

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "volume": item.volume, "has_sound": item.sound is not None}
