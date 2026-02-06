# -*- coding: utf-8 -*-
"""Library handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class LibraryHandler(BaseHandler):
    """Handler for Blender library data type (bpy.data.libraries).

    Libraries are external Blender files linked into the current scene.
    """

    data_type = DataType.LIBRARY

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new library link.

        Args:
            name: Name for new library
            params: Creation parameters:
                - filepath: Path to external Blender file (.blend)

        Returns:
            Dict with created library info
        """
        import bpy  # type: ignore

        filepath = params.get("filepath")
        if not filepath:
            raise ValueError("filepath parameter required for library creation")

        library = bpy.data.libraries.new(name=name, filepath=filepath)
        return {"name": library.name, "filepath": library.filepath}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read library properties.

        Args:
            name: Name of library
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with library properties
        """
        import bpy  # type: ignore

        library = bpy.data.libraries.get(name)
        if library is None:
            raise KeyError(f"Library '{name}' not found")

        if path:
            value = self._get_nested_attr(library, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": library.name,
            "filepath": library.filepath,
            "loaded": library.loaded,
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a library.

        Args:
            name: Name of library
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        library = bpy.data.libraries.get(name)
        if library is None:
            raise KeyError(f"Library '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(library, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a library link.

        Args:
            name: Name of library to delete
            params: Deletion parameters

        Returns:
            Dict with deleted library name
        """
        import bpy  # type: ignore

        library = bpy.data.libraries.get(name)
        if library is None:
            raise KeyError(f"Library '{name}' not found")

        bpy.data.libraries.remove(library)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all libraries.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [
            {"name": l.name, "filepath": l.filepath, "loaded": l.loaded}
            for l in bpy.data.libraries
        ]
        return {"items": items, "count": len(items)}
