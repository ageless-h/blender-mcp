# -*- coding: utf-8 -*-
"""Modifier handler for attached type access."""

from __future__ import annotations

from typing import Any

from ...metadata import (
    get_all_supported_properties,
    get_blender_version,
    get_readable_properties,
    resolve_property_path,
)
from ..base import BaseHandler
from ..registry import HandlerRegistry
from ..types import DataType


@HandlerRegistry.register
class ModifierHandler(BaseHandler):
    """Handler for modifier attached type (object.modifiers access)."""

    data_type = DataType.MODIFIER

    def _resolve_property_container(self, modifier: Any, prop_name: str) -> tuple[Any, str]:
        """Resolve the correct container and property name for a modifier property.

        Uses the metadata system for version-aware property resolution.
        Falls back to direct property access if not in registry.
        """
        mod_type = modifier.type
        version = get_blender_version()

        resolved = resolve_property_path(mod_type, "modifier", prop_name, version)
        if resolved is None:
            resolved = resolve_property_path(mod_type, "physics", prop_name, version)

        if resolved is not None:
            container_path, actual_prop = resolved
            if container_path:
                container = self._get_nested_attr(modifier, container_path)
            else:
                container = modifier
            return container, actual_prop

        if mod_type == "MIRROR" and prop_name in ("use_x", "use_y", "use_z"):
            if version >= (5, 0, 0):
                axis_index = {"use_x": 0, "use_y": 1, "use_z": 2}[prop_name]
                return modifier.use_axis, axis_index
            return modifier, prop_name

        return modifier, prop_name

    def _set_modifier_property(self, modifier: Any, prop_name: str, value: Any) -> bool:
        """Set a property on a modifier, handling nested containers.

        Args:
            modifier: The modifier object
            prop_name: The property name to set
            value: The value to set

        Returns:
            True if property was set successfully
        """
        container, actual_prop = self._resolve_property_container(modifier, prop_name)

        if isinstance(actual_prop, int):
            try:
                container[actual_prop] = value
                return True
            except (TypeError, KeyError, IndexError):
                pass

        prop_name_str = str(actual_prop)
        if hasattr(container, prop_name_str):
            setattr(container, prop_name_str, value)
            return True

        return False

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new modifier on an object.

        Args:
            name: Name for the new modifier
            params: Creation parameters:
                - object: Name of the parent object (required)
                - type: Modifier type (SUBSURF, ARRAY, MIRROR, etc.)

        Returns:
            Dict with created modifier info
        """
        import bpy  # type: ignore

        object_name = params.get("object")
        if not object_name:
            raise ValueError("'object' parameter is required for modifier creation")

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")

        modifier_type = params.get("type", "SUBSURF")
        modifier = obj.modifiers.new(name=name, type=modifier_type)

        settings = params.get("settings", {})
        for key, value in settings.items():
            self._set_modifier_property(modifier, key, value)

        return {
            "name": modifier.name,
            "type": modifier.type,
            "object": object_name,
        }

    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        """Read modifier properties.

        Args:
            name: Name of the modifier
            path: Optional property path
            params: Read parameters:
                - object: Name of the parent object (required)

        Returns:
            Dict with modifier properties
        """
        import bpy  # type: ignore

        object_name = params.get("object")
        if not object_name:
            raise ValueError("'object' parameter is required for modifier read")

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")

        modifier = obj.modifiers.get(name)
        if modifier is None:
            raise KeyError(f"Modifier '{name}' not found on object '{object_name}'")

        if path:
            value = self._get_nested_attr(modifier, path)
            if hasattr(value, "__iter__") and not isinstance(value, str):
                try:
                    value = list(value)
                except TypeError:
                    pass
            return {"name": name, "object": object_name, "path": path, "value": value}

        mod_type = modifier.type
        version = get_blender_version()

        result = {
            "name": modifier.name,
            "type": mod_type,
            "object": object_name,
            "show_viewport": modifier.show_viewport,
            "show_render": modifier.show_render,
            "show_in_editmode": modifier.show_in_editmode,
        }

        # Try to use metadata system for dynamic property reading
        readable_props = get_readable_properties(mod_type, "modifier")
        if readable_props:
            # Use metadata-driven property reading
            supported = get_all_supported_properties(mod_type, "modifier", version)
            for prop_name in readable_props:
                if prop_name not in supported:
                    continue
                try:
                    container, actual_prop = self._resolve_property_container(modifier, prop_name)
                    if isinstance(actual_prop, int):
                        # Array index access (e.g., use_axis[0])
                        value = container[actual_prop]
                    elif hasattr(container, str(actual_prop)):
                        value = getattr(container, str(actual_prop))
                    else:
                        continue
                    # Convert object references to names
                    if hasattr(value, "name") and hasattr(value, "type"):
                        value = value.name
                    elif hasattr(value, "__iter__") and not isinstance(value, str):
                        try:
                            value = list(value)
                        except TypeError:
                            pass
                    result[prop_name] = value
                except (AttributeError, KeyError, IndexError, TypeError):
                    pass
        else:
            # Fallback to hardcoded property reading for unregistered modifier types
            if mod_type == "SUBSURF":
                result["levels"] = modifier.levels
                result["render_levels"] = modifier.render_levels
            elif mod_type == "ARRAY":
                result["count"] = modifier.count
                result["use_relative_offset"] = modifier.use_relative_offset
            elif mod_type == "MIRROR":
                result["use_axis"] = [modifier.use_axis[0], modifier.use_axis[1], modifier.use_axis[2]]
            elif mod_type == "BOOLEAN":
                result["operation"] = modifier.operation
                result["object"] = modifier.object.name if modifier.object else None
            elif mod_type == "SOLIDIFY":
                result["thickness"] = modifier.thickness
                result["offset"] = modifier.offset
            elif mod_type == "BEVEL":
                result["width"] = modifier.width
                result["segments"] = modifier.segments

        return result

    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Write properties to a modifier.

        Args:
            name: Name of the modifier
            properties: Dict of property paths to values
            params: Write parameters:
                - object: Name of the parent object (required)

        Returns:
            Dict with modified properties list
        """
        import bpy  # type: ignore

        object_name = params.get("object")
        if not object_name:
            raise ValueError("'object' parameter is required for modifier write")

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")

        modifier = obj.modifiers.get(name)
        if modifier is None:
            raise KeyError(f"Modifier '{name}' not found on object '{object_name}'")

        modified = []
        for prop_path, value in properties.items():
            if self._set_modifier_property(modifier, prop_path, value):
                modified.append(prop_path)

        return {"name": name, "object": object_name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a modifier from an object.

        Args:
            name: Name of the modifier to delete
            params: Deletion parameters:
                - object: Name of the parent object (required)

        Returns:
            Dict with deleted modifier name
        """
        import bpy  # type: ignore

        object_name = params.get("object")
        if not object_name:
            raise ValueError("'object' parameter is required for modifier delete")

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")

        modifier = obj.modifiers.get(name)
        if modifier is None:
            raise KeyError(f"Modifier '{name}' not found on object '{object_name}'")

        obj.modifiers.remove(modifier)
        return {"deleted": name, "object": object_name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        """List all modifiers on an object.

        Args:
            filter_params: Filter criteria:
                - object: Name of the parent object (required)
                - type: Filter by modifier type

        Returns:
            Dict with items list
        """
        import bpy  # type: ignore

        filter_params = filter_params or {}
        object_name = filter_params.get("object")

        if not object_name:
            raise ValueError("'object' parameter is required for modifier list")

        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise KeyError(f"Object '{object_name}' not found")

        type_filter = filter_params.get("type")

        items = []
        for modifier in obj.modifiers:
            if type_filter and modifier.type != type_filter.upper():
                continue
            items.append(
                {
                    "name": modifier.name,
                    "type": modifier.type,
                    "show_viewport": modifier.show_viewport,
                    "show_render": modifier.show_render,
                }
            )

        return {"items": items, "count": len(items), "object": object_name}
