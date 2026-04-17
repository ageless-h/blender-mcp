# -*- coding: utf-8 -*-
"""Version-aware property path resolver for handler metadata."""

from __future__ import annotations

from typing import Any

try:
    import bpy
except ImportError:
    bpy = None

from .types import PropertyMetadata


def get_blender_version() -> tuple[int, int, int]:
    """Get the current Blender version as a tuple.

    Returns:
        Blender version as (major, minor, patch) tuple.
        Falls back to (4, 2, 0) if bpy is unavailable.
    """
    if bpy is not None:
        try:
            return bpy.app.version
        except AttributeError:
            pass
    return (4, 2, 0)


def _version_in_range(
    version: tuple[int, int, int],
    version_min: tuple[int, int, int] | None,
    version_max: tuple[int, int, int] | None,
) -> bool:
    """Check if a version falls within the specified range.

    Args:
        version: Version to check.
        version_min: Minimum version (inclusive), or None for no minimum.
        version_max: Maximum version (exclusive), or None for no maximum.

    Returns:
        True if version is within the range.
    """
    if version_min is not None and version < version_min:
        return False
    if version_max is not None and version >= version_max:
        return False
    return True


def resolve_property_path(
    handler_type: str,
    category: str,
    prop_name: str,
    blender_version: tuple[int, int, int] | None = None,
) -> tuple[str, str] | None:
    """Resolve a property name to its Blender API path.

    This function provides version-aware property path resolution,
    handling cases where Blender's API has changed between versions.

    Args:
        handler_type: Handler type (e.g., "CLOTH", "MIRROR").
        category: Category of handler ("modifier", "constraint", "physics").
        prop_name: User-facing property name to resolve.
        blender_version: Blender version to use for resolution.
            If None, uses current Blender version.

    Returns:
        Tuple of (container_path, actual_property_name) if property exists
        and is supported in the given version, or None if not found.

    Example:
        >>> resolve_property_path("MIRROR", "modifier", "use_x")
        # In Blender 4.x: ("", "use_x")
        # In Blender 5.0+: ("", "use_axis")  # Special handling needed
    """
    from .registry import get_handler_metadata

    version = blender_version or get_blender_version()
    metadata = get_handler_metadata(handler_type, category)

    if metadata is None:
        return None

    prop_meta = metadata.properties.get(prop_name)
    if prop_meta is None:
        return None

    # Check version compatibility
    if not _version_in_range(version, prop_meta.version_min, prop_meta.version_max):
        return None

    # Extract container and property name from blender_path
    blender_path = prop_meta.blender_path
    if "." in blender_path:
        container, prop = blender_path.rsplit(".", 1)
        return (container, prop)
    return ("", blender_path)


def resolve_property_value(
    handler_type: str,
    category: str,
    prop_name: str,
    value: Any,
    blender_version: tuple[int, int, int] | None = None,
) -> tuple[str, str, Any] | None:
    """Resolve a property name and value to Blender-compatible form.

    Handles special cases like version-dependent property names and
    value transformations.

    Args:
        handler_type: Handler type (e.g., "CLOTH", "MIRROR").
        category: Category of handler ("modifier", "constraint", "physics").
        prop_name: User-facing property name to resolve.
        value: Property value from user API.
        blender_version: Blender version to use for resolution.

    Returns:
        Tuple of (container_path, actual_property_name, transformed_value)
        or None if property not found or unsupported.
    """
    version = blender_version or get_blender_version()

    # Handle special MIRROR modifier use_axis case for Blender 5.0+
    if handler_type == "MIRROR" and category == "modifier":
        if prop_name in ("use_x", "use_y", "use_z") and version >= (5, 0, 0):
            axis_index = {"use_x": 0, "use_y": 1, "use_z": 2}[prop_name]
            return ("", "use_axis", (axis_index, bool(value)))

    resolved = resolve_property_path(handler_type, category, prop_name, version)
    if resolved is None:
        return None

    container, prop = resolved
    return (container, prop, value)


def get_all_supported_properties(
    handler_type: str,
    category: str,
    blender_version: tuple[int, int, int] | None = None,
) -> dict[str, PropertyMetadata]:
    """Get all properties supported for a handler in a specific Blender version.

    Args:
        handler_type: Handler type (e.g., "CLOTH", "MIRROR").
        category: Category of handler ("modifier", "constraint", "physics").
        blender_version: Blender version to use for filtering.

    Returns:
        Dictionary of property names to their metadata, filtered by
        version compatibility.
    """
    from .registry import get_handler_metadata

    version = blender_version or get_blender_version()
    metadata = get_handler_metadata(handler_type, category)

    if metadata is None:
        return {}

    return {
        name: prop
        for name, prop in metadata.properties.items()
        if _version_in_range(version, prop.version_min, prop.version_max)
    }
