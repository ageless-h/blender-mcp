# -*- coding: utf-8 -*-
"""Volume handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class VolumeHandler(BaseHandler):
    """Handler for Blender volume data type (bpy.data.volumes)."""

    data_type = DataType.VOLUME

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new volume.

        Args:
            name: Name for new volume
            params: Creation parameters:
                - filepath: Path to OpenVDB file

        Returns:
            Dict with created volume info
        """
        import bpy  # type: ignore

        volume = bpy.data.volumes.new(name=name)

        filepath = params.get("filepath")
        if filepath:
            volume.filepath = filepath

        return {"name": volume.name}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read volume properties.

        Args:
            name: Name of volume
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with volume properties
        """
        import bpy  # type: ignore

        volume = bpy.data.volumes.get(name)
        if volume is None:
            raise KeyError(f"Volume '{name}' not found")

        if path:
            value = self._get_nested_attr(volume, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": volume.name,
            "filepath": volume.filepath,
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a volume.

        Args:
            name: Name of volume
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        volume = bpy.data.volumes.get(name)
        if volume is None:
            raise KeyError(f"Volume '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(volume, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a volume.

        Args:
            name: Name of volume to delete
            params: Deletion parameters

        Returns:
            Dict with deleted volume name
        """
        import bpy  # type: ignore

        volume = bpy.data.volumes.get(name)
        if volume is None:
            raise KeyError(f"Volume '{name}' not found")

        bpy.data.volumes.remove(volume)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all volumes.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [{"name": v.name, "filepath": v.filepath} for v in bpy.data.volumes]
        return {"items": items, "count": len(items)}
