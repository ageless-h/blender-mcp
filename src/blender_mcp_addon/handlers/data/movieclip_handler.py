# -*- coding: utf-8 -*-
"""Movie clip handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class MovieClipHandler(BaseHandler):
    """Handler for Blender movie clip data type (bpy.data.movieclips)."""

    data_type = DataType.MOVIECLIP

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new movie clip.

        Args:
            name: Name for new movie clip
            params: Creation parameters:
                - filepath: Path to video file

        Returns:
            Dict with created movie clip info
        """
        import bpy  # type: ignore

        clip = bpy.data.movieclips.new(name=name)

        filepath = params.get("filepath")
        if filepath:
            clip.filepath = filepath

        return {"name": clip.name}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read movie clip properties.

        Args:
            name: Name of movie clip
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with movie clip properties
        """
        import bpy  # type: ignore

        clip = bpy.data.movieclips.get(name)
        if clip is None:
            raise KeyError(f"Movie clip '{name}' not found")

        if path:
            value = self._get_nested_attr(clip, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": clip.name,
            "filepath": clip.filepath,
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a movie clip.

        Args:
            name: Name of movie clip
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        clip = bpy.data.movieclips.get(name)
        if clip is None:
            raise KeyError(f"Movie clip '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(clip, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a movie clip.

        Args:
            name: Name of movie clip to delete
            params: Deletion parameters

        Returns:
            Dict with deleted movie clip name
        """
        import bpy  # type: ignore

        clip = bpy.data.movieclips.get(name)
        if clip is None:
            raise KeyError(f"Movie clip '{name}' not found")

        bpy.data.movieclips.remove(clip)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all movie clips.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [{"name": c.name, "filepath": c.filepath} for c in bpy.data.movieclips]
        return {"items": items, "count": len(items)}
