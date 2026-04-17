# -*- coding: utf-8 -*-
"""Modifier handler for attached type access."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..registry import HandlerRegistry
from ..types import DataType

# Mapping of modifier types to their property containers.
# Some modifiers have properties nested in sub-objects (e.g., physics modifiers).
# Format: {modifier_type: {property_name: (container_path, target_property_name)}}
# container_path uses dot notation for nested access, e.g., "settings" or "settings.point_cache"
# For direct properties with name mapping, container_path is empty string ""
MODIFIER_PROPERTY_PATHS: dict[str, dict[str, tuple[str, str]]] = {
    "CLOTH": {
        # Cloth properties are in modifier.settings
        "mass": ("settings", "mass"),
        "tension_stiffness": ("settings", "tension_stiffness"),
        "compression_stiffness": ("settings", "compression_stiffness"),
        "shear_stiffness": ("settings", "shear_stiffness"),
        "bending_stiffness": ("settings", "bending_stiffness"),
        "damping": ("settings", "damping"),
        "air_damping": ("settings", "air_damping"),
        "vel_damping": ("settings", "vel_damping"),
        "density_target": ("settings", "density_target"),
        "density_strength": ("settings", "density_strength"),
        "voxel_cell_size": ("settings", "voxel_cell_size"),
        "pin_stiffness": ("settings", "pin_stiffness"),
        "shrink_min": ("settings", "shrink_min"),
        "shrink_max": ("settings", "shrink_max"),
        "use_internal_springs": ("settings", "use_internal_springs"),
        "use_pressure": ("settings", "use_pressure"),
        "use_sewing_springs": ("settings", "use_sewing_springs"),
    },
    "SOFT_BODY": {
        # Soft body properties are in modifier.settings
        "mass": ("settings", "mass"),
        "speed": ("settings", "speed"),
        "friction": ("settings", "friction"),
        "use_goal": ("settings", "use_goal"),
        "use_edges": ("settings", "use_edges"),
        "use_stiff_quads": ("settings", "use_stiff_quads"),
        "pull": ("settings", "pull"),
        "push": ("settings", "push"),
        "damping": ("settings", "damping"),
        "spring_stiffness": ("settings", "spring_stiffness"),
        "aero": ("settings", "aero"),
        "bend": ("settings", "bend"),
        "collision_type": ("settings", "collision_type"),
        "ball_size": ("settings", "ball_size"),
        "ball_stiff": ("settings", "ball_stiff"),
        "ball_damp": ("settings", "ball_damp"),
        "effector_weights": ("settings", "effector_weights"),
    },
    "FLUID": {
        # Fluid properties are in modifier.settings
        "domain_type": ("settings", "domain_type"),
        "fluid_type": ("settings", "fluid_type"),
    },
    "WAVE": {
        # Wave properties: amplitude -> height, wavelength -> width (name mapping)
        "amplitude": ("", "height"),
        "wavelength": ("", "width"),
    },
}

# MIRROR modifier axis properties changed in Blender 5.0+
# Old API (4.x): modifier.use_x, modifier.use_y, modifier.use_z
# New API (5.0+): modifier.use_axis[0], modifier.use_axis[1], modifier.use_axis[2]
MIRROR_AXIS_PROPERTIES = ("use_x", "use_y", "use_z")

# Cached Blender version - avoids repeated bpy.app.version calls
_CACHED_BLENDER_VERSION: tuple[int, int, int] | None = None


def _get_blender_version() -> tuple[int, int, int]:
    """Get Blender version as tuple (major, minor, patch). Cached at module level."""
    global _CACHED_BLENDER_VERSION
    if _CACHED_BLENDER_VERSION is not None:
        return _CACHED_BLENDER_VERSION
    try:
        import bpy  # type: ignore

        _CACHED_BLENDER_VERSION = bpy.app.version
    except ImportError:
        _CACHED_BLENDER_VERSION = (0, 0, 0)
    return _CACHED_BLENDER_VERSION


@HandlerRegistry.register
class ModifierHandler(BaseHandler):
    """Handler for modifier attached type (object.modifiers access)."""

    data_type = DataType.MODIFIER

    def _resolve_property_container(self, modifier: Any, prop_name: str) -> tuple[Any, str]:
        """Resolve the correct container and property name for a modifier property.

        Some modifiers have properties nested in sub-objects (e.g., physics modifiers).
        This method handles the resolution transparently.

        Args:
            modifier: The modifier object
            prop_name: The property name to set

        Returns:
            Tuple of (container_object, actual_property_name)
        """
        mod_type = modifier.type

        # Handle MIRROR axis properties for Blender 5.0+
        if mod_type == "MIRROR" and prop_name in MIRROR_AXIS_PROPERTIES:
            version = _get_blender_version()
            if version >= (5, 0, 0):
                # Blender 5.0+ uses use_axis array
                axis_index = MIRROR_AXIS_PROPERTIES.index(prop_name)
                return modifier.use_axis, axis_index
            # Blender 4.x uses use_x, use_y, use_z directly
            return modifier, prop_name

        # Check for known nested property paths
        if mod_type in MODIFIER_PROPERTY_PATHS:
            path_map = MODIFIER_PROPERTY_PATHS[mod_type]
            if prop_name in path_map:
                container_path, target_prop = path_map[prop_name]
                if container_path:
                    container = self._get_nested_attr(modifier, container_path)
                else:
                    container = modifier
                return container, target_prop

        # Default: property is directly on modifier
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

        result = {
            "name": modifier.name,
            "type": modifier.type,
            "object": object_name,
            "show_viewport": modifier.show_viewport,
            "show_render": modifier.show_render,
            "show_in_editmode": modifier.show_in_editmode,
        }

        if modifier.type == "SUBSURF":
            result["levels"] = modifier.levels
            result["render_levels"] = modifier.render_levels
        elif modifier.type == "ARRAY":
            result["count"] = modifier.count
            result["use_relative_offset"] = modifier.use_relative_offset
        elif modifier.type == "MIRROR":
            result["use_axis"] = [modifier.use_axis[0], modifier.use_axis[1], modifier.use_axis[2]]
        elif modifier.type == "BOOLEAN":
            result["operation"] = modifier.operation
            result["object"] = modifier.object.name if modifier.object else None
        elif modifier.type == "SOLIDIFY":
            result["thickness"] = modifier.thickness
            result["offset"] = modifier.offset
        elif modifier.type == "BEVEL":
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
