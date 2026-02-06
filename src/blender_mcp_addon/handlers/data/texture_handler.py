# -*- coding: utf-8 -*-
"""Texture handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class TextureHandler(BaseHandler):
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

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read texture properties.

        Args:
            name: Name of texture
            path: Optional property path
            params: Read parameters

        Returns:
            Dict with texture properties
        """
        import bpy  # type: ignore

        texture = bpy.data.textures.get(name)
        if texture is None:
            raise KeyError(f"Texture '{name}' not found")

        if path:
            value = self._get_nested_attr(texture, path)
            return {"name": name, "path": path, "value": value}

        result = {
            "name": texture.name,
            "type": texture.type,
            "use_color_ramp": texture.use_color_ramp,
        }

        if texture.type == "IMAGE" and texture.image:
            result["image"] = texture.image.name
        elif texture.type in [
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
            if texture.use_color_ramp and texture.color_ramp:
                result["color_ramp_elements"] = len(texture.color_ramp.elements)

        return result

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a texture.

        Args:
            name: Name of texture
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        texture = bpy.data.textures.get(name)
        if texture is None:
            raise KeyError(f"Texture '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(texture, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a texture.

        Args:
            name: Name of texture to delete
            params: Deletion parameters

        Returns:
            Dict with deleted texture name
        """
        import bpy  # type: ignore

        texture = bpy.data.textures.get(name)
        if texture is None:
            raise KeyError(f"Texture '{name}' not found")

        bpy.data.textures.remove(texture)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all textures.

        Args:
            filter_params: Optional filter criteria

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        filter_params = filter_params or {}
        texture_type = filter_params.get("type")

        items = []
        for texture in bpy.data.textures:
            if texture_type and texture.type != texture_type.upper():
                continue
            items.append(
                {
                    "name": texture.name,
                    "type": texture.type,
                }
            )
        return {"items": items, "count": len(items)}
