# -*- coding: utf-8 -*-
"""Metadata registry for handler types with built-in type definitions."""

from __future__ import annotations

from .types import HandlerMetadata, PropertyMetadata

# Global registry: key is f"{category}:{handler_type}"
_REGISTRY: dict[str, HandlerMetadata] = {}


def _make_key(handler_type: str, category: str) -> str:
    """Create registry key from handler type and category."""
    return f"{category}:{handler_type}"


def register_handler_metadata(metadata: HandlerMetadata) -> None:
    """Register handler metadata in the global registry.

    Args:
        metadata: HandlerMetadata instance to register.
    """
    key = _make_key(metadata.handler_type, metadata.category)
    _REGISTRY[key] = metadata


def get_handler_metadata(handler_type: str, category: str) -> HandlerMetadata | None:
    """Retrieve handler metadata from the registry.

    Args:
        handler_type: Type identifier (e.g., "CLOTH", "MIRROR").
        category: Category of handler ("modifier", "constraint", "physics").

    Returns:
        HandlerMetadata if found, None otherwise.
    """
    key = _make_key(handler_type, category)
    return _REGISTRY.get(key)


def get_readable_properties(handler_type: str, category: str) -> tuple[str, ...]:
    """Get readable property names for a handler type.

    Args:
        handler_type: Type identifier (e.g., "CLOTH", "MIRROR").
        category: Category of handler ("modifier", "constraint", "physics").

    Returns:
        Tuple of property names that should be included in read responses.
    """
    metadata = get_handler_metadata(handler_type, category)
    if metadata is None:
        return ()
    return metadata.readable_properties


# =============================================================================
# Built-in Handler Metadata Definitions
# =============================================================================

# Physics Modifiers
_CLOTH_METADATA = HandlerMetadata(
    handler_type="CLOTH",
    category="physics",
    container_path="settings",
    properties={
        "mass": PropertyMetadata(
            name="mass",
            blender_path="settings.mass",
            prop_type="float",
            default=0.3,
            min_value=0.0,
            description="Mass of the cloth in kilograms",
        ),
        "tension_stiffness": PropertyMetadata(
            name="tension_stiffness",
            blender_path="settings.tension_stiffness",
            prop_type="float",
            default=15.0,
            min_value=0.0,
            description="How much the material resists stretching",
        ),
        "compression_stiffness": PropertyMetadata(
            name="compression_stiffness",
            blender_path="settings.compression_stiffness",
            prop_type="float",
            default=15.0,
            min_value=0.0,
            description="How much the material resists compression",
        ),
        "damping": PropertyMetadata(
            name="damping",
            blender_path="settings.damping",
            prop_type="float",
            default=0.0,
            min_value=0.0,
            description="Damping of cloth velocity",
        ),
        "air_damping": PropertyMetadata(
            name="air_damping",
            blender_path="settings.air_damping",
            prop_type="float",
            default=1.0,
            min_value=0.0,
            description="Air resistance",
        ),
        "use_collision": PropertyMetadata(
            name="use_collision",
            blender_path="settings.use_collision",
            prop_type="bool",
            default=True,
            description="Enable collisions with other objects",
        ),
        "use_self_collision": PropertyMetadata(
            name="use_self_collision",
            blender_path="settings.use_self_collision",
            prop_type="bool",
            default=False,
            description="Enable self-collision",
        ),
    },
    readable_properties=(
        "mass",
        "tension_stiffness",
        "compression_stiffness",
        "damping",
        "air_damping",
        "use_collision",
        "use_self_collision",
    ),
)

_SOFT_BODY_METADATA = HandlerMetadata(
    handler_type="SOFT_BODY",
    category="physics",
    container_path="settings",
    properties={
        "mass": PropertyMetadata(
            name="mass",
            blender_path="settings.mass",
            prop_type="float",
            default=0.1,
            min_value=0.001,
            description="Mass of the soft body",
        ),
        "speed": PropertyMetadata(
            name="speed",
            blender_path="settings.speed",
            prop_type="float",
            default=1.0,
            description="Speed multiplier for simulation",
        ),
        "use_goal": PropertyMetadata(
            name="use_goal",
            blender_path="settings.use_goal",
            prop_type="bool",
            default=False,
            description="Use goal positions",
        ),
        "use_edges": PropertyMetadata(
            name="use_edges",
            blender_path="settings.use_edges",
            prop_type="bool",
            default=True,
            description="Use edge springs",
        ),
    },
    readable_properties=("mass", "speed", "use_goal", "use_edges"),
)

_FLUID_METADATA = HandlerMetadata(
    handler_type="FLUID",
    category="physics",
    container_path="settings",
    properties={
        "domain_type": PropertyMetadata(
            name="domain_type",
            blender_path="settings.domain_type",
            prop_type="enum",
            enum_items=("GAS", "LIQUID"),
            default="GAS",
            description="Type of fluid domain",
        ),
        "resolution_max": PropertyMetadata(
            name="resolution_max",
            blender_path="settings.resolution_max",
            prop_type="int",
            default=64,
            min_value=1,
            max_value=10000,
            description="Maximum resolution of the fluid grid",
        ),
        "use_mesh": PropertyMetadata(
            name="use_mesh",
            blender_path="settings.use_mesh",
            prop_type="bool",
            default=False,
            description="Generate mesh from fluid particles",
        ),
    },
    readable_properties=("domain_type", "resolution_max", "use_mesh"),
)

# Physics Force Fields
_WAVE_METADATA = HandlerMetadata(
    handler_type="WAVE",
    category="physics",
    container_path="settings",
    properties={
        "use_normal": PropertyMetadata(
            name="use_normal",
            blender_path="settings.use_normal",
            prop_type="bool",
            default=True,
            description="Use normals for wave displacement",
        ),
        "use_x": PropertyMetadata(
            name="use_x",
            blender_path="settings.use_x",
            prop_type="bool",
            default=True,
            description="Enable wave along X axis",
        ),
        "use_y": PropertyMetadata(
            name="use_y",
            blender_path="settings.use_y",
            prop_type="bool",
            default=True,
            description="Enable wave along Y axis",
        ),
        "time_x": PropertyMetadata(
            name="time_x",
            blender_path="settings.time_x",
            prop_type="float",
            default=0.0,
            description="Time offset for X wave",
        ),
        "time_y": PropertyMetadata(
            name="time_y",
            blender_path="settings.time_y",
            prop_type="float",
            default=0.0,
            description="Time offset for Y wave",
        ),
    },
    readable_properties=("use_normal", "use_x", "use_y", "time_x", "time_y"),
)

# Mesh Modifiers
_MIRROR_METADATA = HandlerMetadata(
    handler_type="MIRROR",
    category="modifier",
    container_path="",
    properties={
        # Blender 4.x uses use_x, use_y, use_z directly
        # Blender 5.0+ uses use_axis array
        "use_x": PropertyMetadata(
            name="use_x",
            blender_path="use_x",
            prop_type="bool",
            default=True,
            version_min=None,
            version_max=(5, 0, 0),  # Only in Blender < 5.0
            description="Mirror across X axis (Blender 4.x)",
        ),
        "use_y": PropertyMetadata(
            name="use_y",
            blender_path="use_y",
            prop_type="bool",
            default=False,
            version_min=None,
            version_max=(5, 0, 0),
            description="Mirror across Y axis (Blender 4.x)",
        ),
        "use_z": PropertyMetadata(
            name="use_z",
            blender_path="use_z",
            prop_type="bool",
            default=False,
            version_min=None,
            version_max=(5, 0, 0),
            description="Mirror across Z axis (Blender 4.x)",
        ),
        "use_axis": PropertyMetadata(
            name="use_axis",
            blender_path="use_axis",
            prop_type="vector",
            default=(True, False, False),
            version_min=(5, 0, 0),  # Only in Blender 5.0+
            version_max=None,
            description="Mirror axis array (Blender 5.0+)",
        ),
        "use_clip": PropertyMetadata(
            name="use_clip",
            blender_path="use_clip",
            prop_type="bool",
            default=False,
            description="Prevent vertices from crossing mirror plane",
        ),
        "mirror_object": PropertyMetadata(
            name="mirror_object",
            blender_path="mirror_object",
            prop_type="object_ref",
            default=None,
            description="Object to use as mirror reference",
        ),
        "use_mirror_merge": PropertyMetadata(
            name="use_mirror_merge",
            blender_path="use_mirror_merge",
            prop_type="bool",
            default=True,
            description="Merge vertices at mirror plane",
        ),
        "merge_threshold": PropertyMetadata(
            name="merge_threshold",
            blender_path="merge_threshold",
            prop_type="float",
            default=0.0001,
            min_value=0.0,
            max_value=1.0,
            description="Distance within which vertices are merged",
        ),
    },
    readable_properties=(
        "use_x",
        "use_y",
        "use_z",
        "use_axis",
        "use_clip",
        "mirror_object",
        "use_mirror_merge",
        "merge_threshold",
    ),
)

_SUBSURF_METADATA = HandlerMetadata(
    handler_type="SUBSURF",
    category="modifier",
    container_path="",
    properties={
        "levels": PropertyMetadata(
            name="levels",
            blender_path="levels",
            prop_type="int",
            default=1,
            min_value=0,
            max_value=12,
            description="Subdivision levels in viewport",
        ),
        "render_levels": PropertyMetadata(
            name="render_levels",
            blender_path="render_levels",
            prop_type="int",
            default=2,
            min_value=0,
            max_value=12,
            description="Subdivision levels for render",
        ),
        "subdivision_type": PropertyMetadata(
            name="subdivision_type",
            blender_path="subdivision_type",
            prop_type="enum",
            enum_items=("CATMULL_CLARK", "SIMPLE"),
            default="CATMULL_CLARK",
            description="Subdivision algorithm",
        ),
        "use_limit_surface": PropertyMetadata(
            name="use_limit_surface",
            blender_path="use_limit_surface",
            prop_type="bool",
            default=False,
            description="Use limit surface for normals",
        ),
    },
    readable_properties=("levels", "render_levels", "subdivision_type", "use_limit_surface"),
)

_ARRAY_METADATA = HandlerMetadata(
    handler_type="ARRAY",
    category="modifier",
    container_path="",
    properties={
        "count": PropertyMetadata(
            name="count",
            blender_path="count",
            prop_type="int",
            default=1,
            min_value=1,
            max_value=1000,
            description="Number of duplicates to create",
        ),
        "fit_type": PropertyMetadata(
            name="fit_type",
            blender_path="fit_type",
            prop_type="enum",
            enum_items=("FIXED_COUNT", "FIT_LENGTH", "FIT_CURVE"),
            default="FIXED_COUNT",
            description="How array length is determined",
        ),
        "relative_offset_displace": PropertyMetadata(
            name="relative_offset_displace",
            blender_path="relative_offset_displace",
            prop_type="vector",
            default=(1.0, 0.0, 0.0),
            description="Relative offset between duplicates",
        ),
        "use_relative_offset": PropertyMetadata(
            name="use_relative_offset",
            blender_path="use_relative_offset",
            prop_type="bool",
            default=True,
            description="Use relative offset",
        ),
        "use_constant_offset": PropertyMetadata(
            name="use_constant_offset",
            blender_path="use_constant_offset",
            prop_type="bool",
            default=False,
            description="Use constant offset",
        ),
        "constant_offset_displace": PropertyMetadata(
            name="constant_offset_displace",
            blender_path="constant_offset_displace",
            prop_type="vector",
            default=(0.0, 0.0, 0.0),
            description="Constant offset between duplicates",
        ),
        "use_object_offset": PropertyMetadata(
            name="use_object_offset",
            blender_path="use_object_offset",
            prop_type="bool",
            default=False,
            description="Use object for offset calculation",
        ),
        "offset_object": PropertyMetadata(
            name="offset_object",
            blender_path="offset_object",
            prop_type="object_ref",
            default=None,
            description="Object to use for offset",
        ),
        "use_merge_vertices": PropertyMetadata(
            name="use_merge_vertices",
            blender_path="use_merge_vertices",
            prop_type="bool",
            default=False,
            description="Merge vertices in adjacent duplicates",
        ),
        "merge_threshold": PropertyMetadata(
            name="merge_threshold",
            blender_path="merge_threshold",
            prop_type="float",
            default=0.01,
            min_value=0.0,
            description="Distance for merging vertices",
        ),
    },
    readable_properties=(
        "count",
        "fit_type",
        "relative_offset_displace",
        "use_relative_offset",
        "use_constant_offset",
        "constant_offset_displace",
        "use_object_offset",
        "offset_object",
        "use_merge_vertices",
        "merge_threshold",
    ),
)

_BOOLEAN_METADATA = HandlerMetadata(
    handler_type="BOOLEAN",
    category="modifier",
    container_path="",
    properties={
        "operation": PropertyMetadata(
            name="operation",
            blender_path="operation",
            prop_type="enum",
            enum_items=("DIFFERENCE", "UNION", "INTERSECT"),
            default="DIFFERENCE",
            description="Boolean operation type",
        ),
        "object": PropertyMetadata(
            name="object",
            blender_path="object",
            prop_type="object_ref",
            default=None,
            description="Object to use for boolean operation",
        ),
        "solver": PropertyMetadata(
            name="solver",
            blender_path="solver",
            prop_type="enum",
            enum_items=("FAST", "EXACT"),
            default="EXACT",
            description="Boolean solver algorithm",
        ),
        "use_self": PropertyMetadata(
            name="use_self",
            blender_path="use_self",
            prop_type="bool",
            default=False,
            description="Allow self-intersection in operand",
        ),
        "use_hole_tolerant": PropertyMetadata(
            name="use_hole_tolerant",
            blender_path="use_hole_tolerant",
            prop_type="bool",
            default=False,
            description="More tolerant to holes in mesh",
        ),
    },
    readable_properties=("operation", "object", "solver", "use_self", "use_hole_tolerant"),
)

_SOLIDIFY_METADATA = HandlerMetadata(
    handler_type="SOLIDIFY",
    category="modifier",
    container_path="",
    properties={
        "thickness": PropertyMetadata(
            name="thickness",
            blender_path="thickness",
            prop_type="float",
            default=0.01,
            description="Thickness of the shell",
        ),
        "offset": PropertyMetadata(
            name="offset",
            blender_path="offset",
            prop_type="float",
            default=-1.0,
            min_value=-1.0,
            max_value=1.0,
            description="Offset along normals (-1 to 1)",
        ),
        "use_even_offset": PropertyMetadata(
            name="use_even_offset",
            blender_path="use_even_offset",
            prop_type="bool",
            default=False,
            description="Maintain even thickness",
        ),
        "use_quality_normals": PropertyMetadata(
            name="use_quality_normals",
            blender_path="use_quality_normals",
            prop_type="bool",
            default=True,
            description="Calculate high quality normals",
        ),
        "use_rim": PropertyMetadata(
            name="use_rim",
            blender_path="use_rim",
            prop_type="bool",
            default=True,
            description="Create rim faces",
        ),
    },
    readable_properties=("thickness", "offset", "use_even_offset", "use_quality_normals", "use_rim"),
)

_BEVEL_METADATA = HandlerMetadata(
    handler_type="BEVEL",
    category="modifier",
    container_path="",
    properties={
        "width": PropertyMetadata(
            name="width",
            blender_path="width",
            prop_type="float",
            default=0.1,
            min_value=0.0,
            description="Bevel width",
        ),
        "segments": PropertyMetadata(
            name="segments",
            blender_path="segments",
            prop_type="int",
            default=1,
            min_value=1,
            max_value=100,
            description="Number of bevel segments",
        ),
        "limit_method": PropertyMetadata(
            name="limit_method",
            blender_path="limit_method",
            prop_type="enum",
            enum_items=("NONE", "ANGLE", "WEIGHT", "VGROUP"),
            default="ANGLE",
            description="Method for limiting bevel edges",
        ),
        "angle_limit": PropertyMetadata(
            name="angle_limit",
            blender_path="angle_limit",
            prop_type="float",
            default=0.523599,  # 30 degrees in radians
            min_value=0.0,
            max_value=3.14159,
            description="Angle limit for beveling",
        ),
        "use_clamp_overlap": PropertyMetadata(
            name="use_clamp_overlap",
            blender_path="use_clamp_overlap",
            prop_type="bool",
            default=False,
            description="Prevent overlapping geometry",
        ),
        "harden_normals": PropertyMetadata(
            name="harden_normals",
            blender_path="harden_normals",
            prop_type="bool",
            default=False,
            description="Harden normals on bevel edges",
        ),
    },
    readable_properties=("width", "segments", "limit_method", "angle_limit", "use_clamp_overlap", "harden_normals"),
)


# Register all built-in metadata
def _register_builtins() -> None:
    """Register all built-in handler metadata."""
    register_handler_metadata(_CLOTH_METADATA)
    register_handler_metadata(_SOFT_BODY_METADATA)
    register_handler_metadata(_FLUID_METADATA)
    register_handler_metadata(_WAVE_METADATA)
    register_handler_metadata(_MIRROR_METADATA)
    register_handler_metadata(_SUBSURF_METADATA)
    register_handler_metadata(_ARRAY_METADATA)
    register_handler_metadata(_BOOLEAN_METADATA)
    register_handler_metadata(_SOLIDIFY_METADATA)
    register_handler_metadata(_BEVEL_METADATA)


# Auto-register on module import
_register_builtins()
