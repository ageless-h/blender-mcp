# -*- coding: utf-8 -*-
"""Annotation handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class AnnotationHandler(GenericCollectionHandler):
    """Handler for Blender annotation data type (bpy.data.annotations)."""

    data_type = DataType.ANNOTATION

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new annotation."""
        import bpy  # type: ignore

        annotation = bpy.data.annotations.new(name=name)
        return {"name": annotation.name}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name}
