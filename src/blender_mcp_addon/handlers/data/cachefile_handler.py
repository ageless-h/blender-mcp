# -*- coding: utf-8 -*-
"""Cache file handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class CacheFileHandler(BaseHandler):
    """Handler for Blender cache file data type (bpy.data.cache_files)."""

    data_type = DataType.CACHE_FILE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new cache file.

        Args:
            name: Name for new cache file
            params: Creation parameters:
                - filepath: Path to cache file

        Returns:
            Dict with created cache file info
        """
        import bpy  # type: ignore

        cache_file = bpy.data.cache_files.new(name=name)

        filepath = params.get("filepath")
        if filepath:
            cache_file.filepath = filepath

        return {"name": cache_file.name}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read cache file properties.

        Args:
            name: Name of cache file
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with cache file properties
        """
        import bpy  # type: ignore

        cache_file = bpy.data.cache_files.get(name)
        if cache_file is None:
            raise KeyError(f"Cache file '{name}' not found")

        if path:
            value = self._get_nested_attr(cache_file, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": cache_file.name,
            "filepath": cache_file.filepath,
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a cache file.

        Args:
            name: Name of cache file
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        cache_file = bpy.data.cache_files.get(name)
        if cache_file is None:
            raise KeyError(f"Cache file '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(cache_file, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a cache file.

        Args:
            name: Name of cache file to delete
            params: Deletion parameters

        Returns:
            Dict with deleted cache file name
        """
        import bpy  # type: ignore

        cache_file = bpy.data.cache_files.get(name)
        if cache_file is None:
            raise KeyError(f"Cache file '{name}' not found")

        bpy.data.cache_files.remove(cache_file)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all cache files.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [{"name": c.name, "filepath": c.filepath} for c in bpy.data.cache_files]
        return {"items": items, "count": len(items)}
