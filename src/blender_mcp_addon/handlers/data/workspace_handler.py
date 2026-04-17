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
        """Create a new workspace.

        Note: Blender does not support programmatic workspace creation via bpy.data.workspaces.new().
        Workspaces must be added via bpy.ops.workspace.append() or created manually in the UI.
        """
        raise NotImplementedError(
            "Workspaces cannot be created programmatically. "
            "Use bpy.ops.workspace.append() to append from a template, "
            "or create manually via the Blender UI."
        )

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name}
