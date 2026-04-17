# -*- coding: utf-8 -*-
"""Movie clip handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class MovieClipHandler(GenericCollectionHandler):
    """Handler for Blender movie clip data type (bpy.data.movieclips)."""

    data_type = DataType.MOVIECLIP

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new movie clip."""
        import bpy  # type: ignore

        filepath = params.get("filepath")
        if not filepath:
            raise ValueError("'filepath' parameter is required for movie clip creation")
        clip = bpy.data.movieclips.load(filepath)
        if name and name != clip.name:
            clip.name = name
        return {"name": clip.name}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": item.filepath}

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": item.filepath}

    def _type_label(self) -> str:
        return "Movie clip"
