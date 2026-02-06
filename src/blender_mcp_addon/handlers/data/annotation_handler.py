# -*- coding: utf-8 -*-
"""Annotation handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class AnnotationHandler(BaseHandler):
    """Handler for Blender annotation data type (bpy.data.annotations)."""

    data_type = DataType.ANNOTATION

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new annotation.

        Args:
            name: Name for new annotation
            params: Creation parameters

        Returns:
            Dict with created annotation info
        """
        import bpy  # type: ignore

        annotation = bpy.data.annotations.new(name=name)
        return {"name": annotation.name}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read annotation properties.

        Args:
            name: Name of annotation
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with annotation properties
        """
        import bpy  # type: ignore

        annotation = bpy.data.annotations.get(name)
        if annotation is None:
            raise KeyError(f"Annotation '{name}' not found")

        if path:
            value = self._get_nested_attr(annotation, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": annotation.name,
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to an annotation.

        Args:
            name: Name of annotation
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        annotation = bpy.data.annotations.get(name)
        if annotation is None:
            raise KeyError(f"Annotation '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(annotation, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete an annotation.

        Args:
            name: Name of annotation to delete
            params: Deletion parameters

        Returns:
            Dict with deleted annotation name
        """
        import bpy  # type: ignore

        annotation = bpy.data.annotations.get(name)
        if annotation is None:
            raise KeyError(f"Annotation '{name}' not found")

        bpy.data.annotations.remove(annotation)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all annotations.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        items = [{"name": a.name} for a in bpy.data.annotations]
        return {"items": items, "count": len(items)}
