# -*- coding: utf-8 -*-
"""Texture handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import GenericCollectionHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class TextureHandler(GenericCollectionHandler):
    """Handler for Blender texture data type (bpy.data.textures)."""

    data_type = DataType.TEXTURE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new texture.

        Args:
            name: Name for new texture
            params: Creation parameters:
                - type: Texture type (IMAGE, BLEND, CLOUDS, WOOD, MARBLE, etc.)
                - width: Image width (for IMAGE type)
                - height: Image height (for IMAGE type)
                - use_color_ramp: Enable color ramp (for some types)

        Returns:
            Dict with created texture info
        """
        import bpy  # type: ignore

        texture_type = params.get("type", "IMAGE")
        texture = bpy.data.textures.new(name=name, type=texture_type)

        if "use_color_ramp" in params:
            texture.use_color_ramp = params["use_color_ramp"]

        if texture_type == "IMAGE":
            if "width" in params:
                texture.image_scale[0] = params["width"]
            if "height" in params:
                texture.image_scale[1] = params["height"]

        return {"name": texture.name, "type": texture.type}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": item.name,
            "type": item.type,
            "use_color_ramp": item.use_color_ramp,
        }

        if item.type == "IMAGE" and item.image:
            result["image"] = item.image.name
        elif item.type in [
            "BLEND",
            "CLOUDS",
            "WOOD",
            "MARBLE",
            "MAGIC",
            "STUCCI",
            "NOISE",
            "VORONOI",
            "MUSGRAVE",
        ]:
            if item.use_color_ramp and item.color_ramp:
                result["color_ramp_elements"] = len(item.color_ramp.elements)

        return result

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "type": item.type}

    def _filter_item(self, item: Any, filter_params: dict[str, Any]) -> bool:
        texture_type = filter_params.get("type")
        if texture_type and item.type != texture_type.upper():
            return False
        return True
