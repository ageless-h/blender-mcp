# -*- coding: utf-8 -*-
"""Light probe handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class LightProbeHandler(BaseHandler):
    """Handler for Blender light probe data type (bpy.data.lightprobes)."""

    data_type = DataType.PROBE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new light probe.

        Args:
            name: Name for new light probe
            params: Creation parameters:
                - type: Probe type (GRID, PLANAR, CUBEMAP)

        Returns:
            Dict with created light probe info
        """
        import bpy  # type: ignore

        probe_type = params.get("type", "CUBEMAP")
        probe = bpy.data.lightprobes.new(name=name, type=probe_type)

        return {"name": probe.name, "type": probe.type}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read light probe properties.

        Args:
            name: Name of light probe
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with light probe properties
        """
        import bpy  # type: ignore

        probe = bpy.data.lightprobes.get(name)
        if probe is None:
            raise KeyError(f"Light probe '{name}' not found")

        if path:
            value = self._get_nested_attr(probe, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": probe.name,
            "type": probe.type,
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a light probe.

        Args:
            name: Name of light probe
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        probe = bpy.data.lightprobes.get(name)
        if probe is None:
            raise KeyError(f"Light probe '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(probe, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a light probe.

        Args:
            name: Name of light probe to delete
            params: Deletion parameters

        Returns:
            Dict with deleted light probe name
        """
        import bpy  # type: ignore

        probe = bpy.data.lightprobes.get(name)
        if probe is None:
            raise KeyError(f"Light probe '{name}' not found")

        bpy.data.lightprobes.remove(probe)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all light probes.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        filter_params = filter_params or {}
        probe_type = filter_params.get("type")

        items = []
        for probe in bpy.data.lightprobes:
            if probe_type and probe.type != probe_type.upper():
                continue
            items.append(
                {
                    "name": probe.name,
                    "type": probe.type,
                }
            )
        return {"items": items, "count": len(items)}
