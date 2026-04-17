# -*- coding: utf-8 -*-
"""Handler Property Metadata System for Blender MCP addon.

This module provides a declarative metadata registry for handler properties,
replacing hardcoded property mappings with version-aware resolution.

Key components:
- PropertyMetadata: Describes a single property's metadata
- HandlerMetadata: Groups properties for a handler type
- resolve_property_path: Version-aware property path resolution
- get_handler_metadata: Retrieve handler metadata from registry

Usage:
    from blender_mcp_addon.metadata import (
        PropertyMetadata,
        HandlerMetadata,
        get_handler_metadata,
        resolve_property_path,
    )

    # Get metadata for MIRROR modifier
    meta = get_handler_metadata("MIRROR", "modifier")

    # Resolve a property path with version awareness
    container, prop = resolve_property_path("MIRROR", "modifier", "use_x")
"""

from __future__ import annotations

from .registry import (
    get_handler_metadata,
    get_readable_properties,
    register_handler_metadata,
)
from .resolver import get_all_supported_properties, get_blender_version, resolve_property_path, resolve_property_value
from .types import HandlerMetadata, PropertyMetadata

__all__ = [
    # Types
    "PropertyMetadata",
    "HandlerMetadata",
    # Registry
    "register_handler_metadata",
    "get_handler_metadata",
    "get_readable_properties",
    # Resolver
    "resolve_property_path",
    "resolve_property_value",
    "get_all_supported_properties",
    "get_blender_version",
]
