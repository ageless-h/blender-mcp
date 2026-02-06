# -*- coding: utf-8 -*-
"""Speaker handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class SpeakerHandler(BaseHandler):
    """Handler for Blender speaker data type (bpy.data.speakers)."""

    data_type = DataType.SPEAKER

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new speaker.

        Args:
            name: Name for new speaker
            params: Creation parameters:
                - volume: Speaker volume

        Returns:
            Dict with created speaker info
        """
        import bpy  # type: ignore

        speaker = bpy.data.speakers.new(name=name)

        if "volume" in params:
            speaker.volume = params["volume"]

        return {"name": speaker.name, "volume": speaker.volume}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read speaker properties.

        Args:
            name: Name of speaker
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with speaker properties
        """
        import bpy  # type: ignore

        speaker = bpy.data.speakers.get(name)
        if speaker is None:
            raise KeyError(f"Speaker '{name}' not found")

        if path:
            value = self._get_nested_attr(speaker, path)
            return {"name": name, "path": path, "value": value}

        result = {
            "name": speaker.name,
            "volume": speaker.volume,
        }

        if speaker.sound:
            result["sound"] = speaker.sound.name

        return result

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a speaker.

        Args:
            name: Name of speaker
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        speaker = bpy.data.speakers.get(name)
        if speaker is None:
            raise KeyError(f"Speaker '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(speaker, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a speaker.

        Args:
            name: Name of speaker to delete
            params: Deletion parameters

        Returns:
            Dict with deleted speaker name
        """
        import bpy  # type: ignore

        speaker = bpy.data.speakers.get(name)
        if speaker is None:
            raise KeyError(f"Speaker '{name}' not found")

        bpy.data.speakers.remove(speaker)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all speakers.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [
            {"name": s.name, "volume": s.volume, "has_sound": s.sound is not None}
            for s in bpy.data.speakers
        ]
        return {"items": items, "count": len(items)}
