# -*- coding: utf-8 -*-
"""Key/Shape Keys handler for unified CRUD operations."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..types import DataType
from ..registry import HandlerRegistry


@HandlerRegistry.register
class KeyHandler(BaseHandler):
    """Handler for Blender key/shape keys data.

    Note: Shape Keys are attached properties of objects, not standalone bpy.data blocks.
    This handler reads shape keys from objects.
    """

    data_type = DataType.KEY

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new shape key block.

        Args:
            name: Name for new shape key
            params: Creation parameters:
                - object: Object name to add shape key to
                - value: Initial value for shape key

        Returns:
            Dict with created shape key info
        """
        import bpy  # type: ignore

        object_name = params.get("object")
        if not object_name:
            raise ValueError("object parameter required for shape key creation")

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")

        if obj.data is None:
            raise ValueError(f"Object '{object_name}' has no data block")

        if not hasattr(obj.data, "shape_keys"):
            raise ValueError(
                f"Object '{object_name}' data type does not support shape keys"
            )

        shape_key = obj.data.shape_keys.key_blocks.get(name)
        if shape_key is None:
            obj.data.shape_keys.key_blocks.new(name=name)

        return {"name": name, "object": object_name}

    def read(
        self, name: str, path: str | None, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Read shape key properties.

        Args:
            name: Name of shape key
            path: Optional property path
            params: Read parameters:
                - object: Object name containing the shape key (required)

        Returns:
            Dict with shape key properties
        """
        import bpy  # type: ignore

        object_name = params.get("object")
        if not object_name:
            raise ValueError("object parameter required for shape key read")

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")

        if obj.data is None or not hasattr(obj.data, "shape_keys"):
            raise ValueError(f"Object '{object_name}' does not support shape keys")

        shape_key = obj.data.shape_keys.key_blocks.get(name)
        if shape_key is None:
            raise KeyError(f"Shape key '{name}' not found on object '{object_name}'")

        if path:
            value = self._get_nested_attr(shape_key, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": shape_key.name,
            "value": shape_key.value,
            "vertex_group": shape_key.vertex_group,
            "relative": shape_key.relative,
            "mute": shape_key.mute,
        }

    def write(
        self, name: str, properties: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Write properties to a shape key.

        Args:
            name: Name of shape key
            properties: Dict of property paths to values
            params: Write parameters:
                - object: Object name containing the shape key (required)

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        object_name = params.get("object")
        if not object_name:
            raise ValueError("object parameter required for shape key write")

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")

        if obj.data is None or not hasattr(obj.data, "shape_keys"):
            raise ValueError(f"Object '{object_name}' does not support shape keys")

        shape_key = obj.data.shape_keys.key_blocks.get(name)
        if shape_key is None:
            raise KeyError(f"Shape key '{name}' not found on object '{object_name}'")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(shape_key, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a shape key.

        Args:
            name: Name of shape key to delete
            params: Deletion parameters:
                - object: Object name containing the shape key (required)

        Returns:
            Dict with deleted shape key name
        """
        import bpy  # type: ignore

        object_name = params.get("object")
        if not object_name:
            raise ValueError("object parameter required for shape key deletion")

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")

        if obj.data is None or not hasattr(obj.data, "shape_keys"):
            raise ValueError(f"Object '{object_name}' does not support shape keys")

        shape_key = obj.data.shape_keys.key_blocks.get(name)
        if shape_key is None:
            raise KeyError(f"Shape key '{name}' not found on object '{object_name}'")

        obj.data.shape_keys.key_blocks.remove(shape_key)
        return {"deleted": name, "object": object_name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all shape keys for an object.

        Args:
            filter_params: Optional filter criteria:
                - object: Object name to list shape keys for (required)

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        filter_params = filter_params or {}
        object_name = filter_params.get("object")

        if not object_name:
            raise ValueError("object parameter required for shape key list")

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")

        if obj.data is None or not hasattr(obj.data, "shape_keys"):
            return {"items": [], "count": 0}

        items = [
            {"name": k.name, "value": k.value} for k in obj.data.shape_keys.key_blocks
        ]
        return {"items": items, "count": len(items)}
