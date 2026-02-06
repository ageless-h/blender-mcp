# -*- coding: utf-8 -*-
"""Workspace handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class WorkspaceHandler(BaseHandler):
    """Handler for Blender workspace data type (bpy.data.workspaces)."""

    data_type = DataType.WORKSPACE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new workspace.

        Args:
            name: Name for new workspace
            params: Creation parameters

        Returns:
            Dict with created workspace info
        """
        import bpy  # type: ignore

        workspace = bpy.data.workspaces.new(name=name)
        return {"name": workspace.name}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read workspace properties.

        Args:
            name: Name of workspace
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with workspace properties
        """
        import bpy  # type: ignore

        workspace = bpy.data.workspaces.get(name)
        if workspace is None:
            raise KeyError(f"Workspace '{name}' not found")

        if path:
            value = self._get_nested_attr(workspace, path)
            return {"name": name, "path": path, "value": value}

        result = {
            "name": workspace.name,
        }

        return result

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a workspace.

        Args:
            name: Name of workspace
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        workspace = bpy.data.workspaces.get(name)
        if workspace is None:
            raise KeyError(f"Workspace '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(workspace, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a workspace.

        Args:
            name: Name of workspace to delete
            params: Deletion parameters

        Returns:
            Dict with deleted workspace name
        """
        import bpy  # type: ignore

        workspace = bpy.data.workspaces.get(name)
        if workspace is None:
            raise KeyError(f"Workspace '{name}' not found")

        bpy.data.workspaces.remove(workspace)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all workspaces.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [{"name": w.name} for w in bpy.data.workspaces]
        return {"items": items, "count": len(items)}
