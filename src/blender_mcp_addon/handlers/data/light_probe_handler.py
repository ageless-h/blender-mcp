# -*- coding: utf-8 -*-
"""Light probe handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class LightProbeHandler(GenericCollectionHandler):
    """Handler for Blender light probe data type (bpy.data.lightprobes)."""

    data_type = DataType.PROBE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new light probe."""
        import bpy  # type: ignore

        probe_type = params.get("type", "CUBEMAP")
        probe = bpy.data.lightprobes.new(name=name, type=probe_type)
        return {"name": probe.name, "type": probe.type}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "type": item.type}

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "type": item.type}

    def _type_label(self) -> str:
        return "Light probe"

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List light probes, with optional type filter."""
        filter_params = filter_params or {}
        probe_type = filter_params.get("type")

        collection = self.get_collection()
        if collection is None:
            return {"items": [], "count": 0}

        items = []
        for probe in collection:
            if probe_type and probe.type != probe_type.upper():
                continue
            items.append(self._list_fields(probe))
        return {"items": items, "count": len(items)}
