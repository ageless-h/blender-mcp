# -*- coding: utf-8 -*-
"""Image handler for unified CRUD operations with base64 support."""
from __future__ import annotations

import base64
from typing import Any

from ..base import BaseHandler
from ..registry import HandlerRegistry
from ..types import DataType


def image_list(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Standalone image list for blender.get_images capability."""
    import fnmatch as _fnmatch

    import bpy  # type: ignore

    from ..response import _ok

    filter_mode = payload.get("filter", "all")
    name_pattern = payload.get("name_pattern")

    items = []
    for image in bpy.data.images:
        # Apply filter
        if filter_mode == "packed" and not image.packed_file:
            continue
        elif filter_mode == "external" and (image.packed_file or image.source == "GENERATED"):
            continue
        elif filter_mode == "missing" and (image.packed_file or not image.filepath or image.has_data):
            continue
        elif filter_mode == "unused" and image.users > 0:
            continue

        # Apply name pattern
        if name_pattern and not _fnmatch.fnmatch(image.name, name_pattern):
            continue

        items.append({
            "name": image.name,
            "width": image.size[0],
            "height": image.size[1],
            "filepath": image.filepath,
            "source": image.source,
            "packed": image.packed_file is not None,
            "colorspace": image.colorspace_settings.name if hasattr(image, "colorspace_settings") else "",
            "users": image.users,
        })

    return _ok(result={"images": items, "count": len(items)}, started=started)


@HandlerRegistry.register
class ImageHandler(BaseHandler):
    """Handler for Blender image data type (bpy.data.images)."""

    data_type = DataType.IMAGE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new image.

        Args:
            name: Name for the new image
            params: Creation parameters:
                - width: Image width (default: 1024)
                - height: Image height (default: 1024)
                - color: Fill color as [r, g, b, a]
                - float_buffer: Use 32-bit float buffer
                - alpha: Include alpha channel

        Returns:
            Dict with created image info
        """
        import bpy  # type: ignore

        width = params.get("width", 1024)
        height = params.get("height", 1024)
        alpha = params.get("alpha", True)
        float_buffer = params.get("float_buffer", False)

        image = bpy.data.images.new(
            name=name,
            width=width,
            height=height,
            alpha=alpha,
            float_buffer=float_buffer,
        )

        color = params.get("color")
        if color:
            pixels = list(image.pixels)
            for i in range(0, len(pixels), 4):
                pixels[i] = color[0]
                pixels[i + 1] = color[1]
                pixels[i + 2] = color[2]
                if len(color) > 3:
                    pixels[i + 3] = color[3]
            image.pixels[:] = pixels

        return {
            "name": image.name,
            "type": "image",
            "width": image.size[0],
            "height": image.size[1],
        }

    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read image properties with optional base64 encoding.

        Args:
            name: Name of the image
            path: Optional property path
            params: Read parameters:
                - format: "base64" to get image data as base64
                - scale: Scale factor for output (0.0-1.0)

        Returns:
            Dict with image properties and optionally base64 data
        """
        import bpy  # type: ignore

        image = bpy.data.images.get(name)
        if image is None:
            raise KeyError(f"Image '{name}' not found")

        if path:
            value = self._get_nested_attr(image, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            return {"name": name, "path": path, "value": value}

        result = {
            "name": image.name,
            "width": image.size[0],
            "height": image.size[1],
            "channels": image.channels,
            "depth": image.depth,
            "is_float": image.is_float,
            "filepath": image.filepath,
            "source": image.source,
            "type": image.type,
            "users": image.users,
        }

        output_format = params.get("format")
        if output_format == "base64":
            result["base64"] = self._image_to_base64(image, params)

        return result

    def _image_to_base64(self, image: Any, params: dict[str, Any]) -> str:
        """Convert image to base64 string.

        Args:
            image: Blender image object
            params: Conversion parameters:
                - scale: Scale factor (0.0-1.0)
                - file_format: Output format (PNG, JPEG, etc.)

        Returns:
            Base64 encoded string
        """
        import os
        import tempfile

        import bpy  # type: ignore

        scale = params.get("scale", 1.0)
        file_format = params.get("file_format", "PNG")

        scene = bpy.context.scene
        original_format = scene.render.image_settings.file_format
        original_quality = scene.render.image_settings.quality

        scene.render.image_settings.file_format = file_format
        if file_format == "JPEG":
            scene.render.image_settings.quality = params.get("quality", 90)

        with tempfile.NamedTemporaryFile(suffix=f".{file_format.lower()}", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            if scale != 1.0:
                width = int(image.size[0] * scale)
                height = int(image.size[1] * scale)
                image.scale(width, height)

            image.save_render(tmp_path)

            with open(tmp_path, "rb") as f:
                data = f.read()

            return base64.b64encode(data).decode("utf-8")
        finally:
            scene.render.image_settings.file_format = original_format
            scene.render.image_settings.quality = original_quality
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write properties to an image.

        Args:
            name: Name of the image
            properties: Dict of property paths to values
            params: Write parameters

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        image = bpy.data.images.get(name)
        if image is None:
            raise KeyError(f"Image '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            if prop_path == "filepath":
                image.filepath = value
                modified.append("filepath")
            elif prop_path == "pack":
                if value:
                    image.pack()
                    modified.append("pack")
            elif prop_path == "unpack":
                if value:
                    image.unpack()
                    modified.append("unpack")
            elif prop_path == "reload":
                if value:
                    image.reload()
                    modified.append("reload")
            else:
                self._set_nested_attr(image, prop_path, value)
                modified.append(prop_path)

        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete an image.

        Args:
            name: Name of the image to delete
            params: Deletion parameters

        Returns:
            Dict with deleted image name
        """
        import bpy  # type: ignore

        image = bpy.data.images.get(name)
        if image is None:
            raise KeyError(f"Image '{name}' not found")

        bpy.data.images.remove(image)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all images.

        Args:
            filter_params: Optional filter criteria:
                - source: Filter by source type (FILE, GENERATED, etc.)

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        filter_params = filter_params or {}
        source_filter = filter_params.get("source")

        items = []
        for image in bpy.data.images:
            if source_filter and image.source != source_filter:
                continue
            items.append({
                "name": image.name,
                "width": image.size[0],
                "height": image.size[1],
                "source": image.source,
                "users": image.users,
            })

        return {"items": items, "count": len(items)}
