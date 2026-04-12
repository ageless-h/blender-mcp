# -*- coding: utf-8 -*-
"""Library handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class LibraryHandler(GenericCollectionHandler):
    """Handler for Blender library data type (bpy.data.libraries).

    Libraries are external Blender files linked into the current scene.
    """

    data_type = DataType.LIBRARY

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new library link."""
        import bpy  # type: ignore

        filepath = params.get("filepath")
        if not filepath:
            raise ValueError("filepath parameter required for library creation")

        library = bpy.data.libraries.new(name=name, filepath=filepath)
        return {"name": library.name, "filepath": library.filepath}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {
            "name": item.name,
            "filepath": item.filepath,
            "loaded": item.loaded,
        }

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": item.filepath, "loaded": item.loaded}
