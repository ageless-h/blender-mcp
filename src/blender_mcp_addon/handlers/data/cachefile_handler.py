# -*- coding: utf-8 -*-
"""Cache file handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class CacheFileHandler(GenericCollectionHandler):
    """Handler for Blender cache file data type (bpy.data.cache_files)."""

    data_type = DataType.CACHE_FILE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new cache file."""
        import bpy  # type: ignore

        cache_file = bpy.data.cache_files.new(name=name)
        filepath = params.get("filepath")
        if filepath:
            cache_file.filepath = filepath
        return {"name": cache_file.name}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": item.filepath}

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": item.filepath}

    def _type_label(self) -> str:
        return "Cache file"
