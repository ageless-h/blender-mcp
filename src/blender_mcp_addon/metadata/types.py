# -*- coding: utf-8 -*-
"""Data structures for handler property metadata system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PropertyMetadata:
    """Metadata for a single handler property.

    Describes how a user-facing API property maps to Blender's internal
    property path, including type information, constraints, and version
    compatibility.

    Attributes:
        name: User API property name (e.g., "mass").
        blender_path: Blender API path relative to container (e.g., "settings.mass").
        prop_type: Property type - "float", "int", "bool", "enum", "vector", or "object_ref".
        default: Default value for the property.
        min_value: Minimum value for numeric types.
        max_value: Maximum value for numeric types.
        enum_items: Valid enum values as tuple of strings.
        version_min: Minimum Blender version that supports this property.
        version_max: Maximum Blender version (exclusive) that supports this property.
        description: Human-readable description of the property.
    """

    name: str  # User API property name (e.g., "mass")
    blender_path: str  # Blender API path (e.g., "settings.mass")
    prop_type: str  # "float" | "int" | "bool" | "enum" | "vector" | "object_ref"
    default: Any = None
    min_value: float | None = None
    max_value: float | None = None
    enum_items: tuple[str, ...] | None = None
    version_min: tuple[int, int, int] | None = None
    version_max: tuple[int, int, int] | None = None
    description: str = ""


@dataclass
class HandlerMetadata:
    """Metadata for a complete handler type.

    Groups all property metadata for a specific handler type (modifier,
    constraint, physics, etc.) with category and container information.

    Attributes:
        handler_type: Type identifier (e.g., "CLOTH", "MIRROR", "COPY_LOCATION").
        category: Category of handler - "modifier", "constraint", or "physics".
        container_path: Default container path for property access (e.g., "settings").
        properties: Dictionary mapping property names to their metadata.
        readable_properties: Tuple of property names that should be included in read responses.
    """

    handler_type: str  # "CLOTH" | "MIRROR" | "COPY_LOCATION" etc
    category: str  # "modifier" | "constraint" | "physics"
    container_path: str  # Default container path (e.g., "settings")
    properties: dict[str, PropertyMetadata] = field(default_factory=dict)
    readable_properties: tuple[str, ...] = ()
