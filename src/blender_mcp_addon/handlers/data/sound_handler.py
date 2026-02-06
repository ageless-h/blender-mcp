# -*- coding: utf-8 -*-
"""Sound handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class SoundHandler(BaseHandler):
    """Handler for Blender sound data type (bpy.data.sounds)."""

    data_type = DataType.SOUND

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new sound.

        Args:
            name: Name for new sound
            params: Creation parameters:
                - filepath: Path to audio file

        Returns:
            Dict with created sound info
        """
        import bpy  # type: ignore

        sound = bpy.data.sounds.new(name=name)

        filepath = params.get("filepath")
        if filepath:
            sound.filepath = filepath

        return {"name": sound.name}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read sound properties.

        Args:
            name: Name of sound
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with sound properties
        """
        import bpy  # type: ignore

        sound = bpy.data.sounds.get(name)
        if sound is None:
            raise KeyError(f"Sound '{name}' not found")

        if path:
            value = self._get_nested_attr(sound, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": sound.name,
            "filepath": sound.filepath,
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a sound.

        Args:
            name: Name of sound
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        sound = bpy.data.sounds.get(name)
        if sound is None:
            raise KeyError(f"Sound '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(sound, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a sound.

        Args:
            name: Name of sound to delete
            params: Deletion parameters

        Returns:
            Dict with deleted sound name
        """
        import bpy  # type: ignore

        sound = bpy.data.sounds.get(name)
        if sound is None:
            raise KeyError(f"Sound '{name}' not found")

        bpy.data.sounds.remove(sound)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all sounds.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [{"name": s.name, "filepath": s.filepath} for s in bpy.data.sounds]
        return {"items": items, "count": len(items)}
