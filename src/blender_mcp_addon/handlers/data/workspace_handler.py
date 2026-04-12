# -*- coding: utf-8 -*-
"""Workspace handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class WorkspaceHandler(GenericCollectionHandler):
    """Handler for Blender workspace data type (bpy.data.workspaces)."""

    data_type = DataType.WORKSPACE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new workspace."""
        import bpy  # type: ignore

        workspace = bpy.data.workspaces.new(name=name)
        return {"name": workspace.name}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name}
