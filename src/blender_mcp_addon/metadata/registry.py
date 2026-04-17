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

_RIGID_BODY_METADATA = HandlerMetadata(
    handler_type="RIGID_BODY",
    category="physics",
    container_path="rigid_body",
    properties={
        "type": PropertyMetadata(
            name="type",
            blender_path="rigid_body.type",
            prop_type="enum",
            enum_items=("ACTIVE", "PASSIVE"),
            default="ACTIVE",
            description="Rigid body type",
        ),
        "mass": PropertyMetadata(
            name="mass",
            blender_path="rigid_body.mass",
            prop_type="float",
            default=1.0,
            min_value=0.0,
            description="Mass of the rigid body",
        ),
        "friction": PropertyMetadata(
            name="friction",
            blender_path="rigid_body.friction",
            prop_type="float",
            default=0.5,
            min_value=0.0,
            max_value=1.0,
            description="Friction coefficient",
        ),
        "restitution": PropertyMetadata(
            name="restitution",
            blender_path="rigid_body.restitution",
            prop_type="float",
            default=0.0,
            min_value=0.0,
            max_value=1.0,
            description="Bounciness",
        ),
        "use_margin": PropertyMetadata(
            name="use_margin",
            blender_path="rigid_body.use_margin",
            prop_type="bool",
            default=False,
            description="Use collision margin",
        ),
        "collision_margin": PropertyMetadata(
            name="collision_margin",
            blender_path="rigid_body.collision_margin",
            prop_type="float",
            default=0.0,
            min_value=0.0,
            description="Collision margin distance",
        ),
        "collision_shape": PropertyMetadata(
            name="collision_shape",
            blender_path="rigid_body.collision_shape",
            prop_type="enum",
            enum_items=("BOX", "SPHERE", "CAPSULE", "CYLINDER", "CONE", "CONVEX_HULL", "MESH", "COMPOUND"),
            default="BOX",
            description="Collision shape type",
        ),
        "use_deactivation": PropertyMetadata(
            name="use_deactivation",
            blender_path="rigid_body.use_deactivation",
            prop_type="bool",
            default=True,
            description="Enable deactivation",
        ),
        "angular_damping": PropertyMetadata(
            name="angular_damping",
            blender_path="rigid_body.angular_damping",
            prop_type="float",
            default=0.1,
            min_value=0.0,
            max_value=1.0,
            description="Angular damping",
        ),
        "linear_damping": PropertyMetadata(
            name="linear_damping",
            blender_path="rigid_body.linear_damping",
            prop_type="float",
            default=0.04,
            min_value=0.0,
            max_value=1.0,
            description="Linear damping",
        ),
    },
    readable_properties=(
        "type",
        "mass",
        "friction",
        "restitution",
        "use_margin",
        "collision_margin",
        "collision_shape",
        "use_deactivation",
        "angular_damping",
        "linear_damping",
    ),
)

_PARTICLE_METADATA = HandlerMetadata(
    handler_type="PARTICLE",
    category="physics",
    container_path="settings",
    properties={
        "count": PropertyMetadata(
            name="count",
            blender_path="settings.count",
            prop_type="int",
            default=1000,
            min_value=0,
            description="Number of particles",
        ),
        "lifetime": PropertyMetadata(
            name="lifetime",
            blender_path="settings.lifetime",
            prop_type="float",
            default=50.0,
            min_value=0.0,
            description="Particle lifetime in frames",
        ),
        "start_frame": PropertyMetadata(
            name="start_frame",
            blender_path="settings.frame_start",
            prop_type="float",
            default=1.0,
            description="Start frame for emission",
        ),
        "end_frame": PropertyMetadata(
            name="end_frame",
            blender_path="settings.frame_end",
            prop_type="float",
            default=200.0,
            description="End frame for emission",
        ),
        "emit_from": PropertyMetadata(
            name="emit_from",
            blender_path="settings.emit_from",
            prop_type="enum",
            enum_items=("VERT", "FACE", "VOLUME"),
            default="FACE",
            description="Emission source",
        ),
        "use_emit_random": PropertyMetadata(
            name="use_emit_random",
            blender_path="settings.use_emit_random",
            prop_type="bool",
            default=True,
            description="Random emission order",
        ),
        "normal_factor": PropertyMetadata(
            name="normal_factor",
            blender_path="settings.normal_factor",
            prop_type="float",
            default=0.0,
            description="Normal velocity factor",
        ),
        "use_size": PropertyMetadata(
            name="use_size",
            blender_path="settings.use_size",
            prop_type="bool",
            default=True,
            description="Use particle size",
        ),
        "size": PropertyMetadata(
            name="size",
            blender_path="settings.size",
            prop_type="float",
            default=0.05,
            min_value=0.0,
            description="Particle size",
        ),
    },
    readable_properties=(
        "count",
        "lifetime",
        "start_frame",
        "end_frame",
        "emit_from",
        "use_emit_random",
        "normal_factor",
        "use_size",
        "size",
    ),
)

_FORCE_FIELD_METADATA = HandlerMetadata(
    handler_type="FORCE_FIELD",
    category="physics",
    container_path="field",
    properties={
        "type": PropertyMetadata(
            name="type",
            blender_path="field.type",
            prop_type="enum",
            enum_items=(
                "NONE",
                "WIND",
                "FORCE",
                "VORTEX",
                "MAGNET",
                "HARMONIC",
                "CHARGE",
                "DRAG",
                "TURBULENCE",
                "BOID",
            ),
            default="FORCE",
            description="Force field type",
        ),
        "strength": PropertyMetadata(
            name="strength",
            blender_path="field.strength",
            prop_type="float",
            default=1.0,
            description="Field strength",
        ),
        "falloff_type": PropertyMetadata(
            name="falloff_type",
            blender_path="field.falloff_type",
            prop_type="enum",
            enum_items=("SPHERE", "TUBE", "CONE"),
            default="SPHERE",
            description="Falloff shape",
        ),
        "falloff_power": PropertyMetadata(
            name="falloff_power",
            blender_path="field.falloff_power",
            prop_type="float",
            default=2.0,
            min_value=0.0,
            description="Falloff power",
        ),
        "use_max_distance": PropertyMetadata(
            name="use_max_distance",
            blender_path="field.use_max_distance",
            prop_type="bool",
            default=False,
            description="Use maximum distance",
        ),
        "max_distance": PropertyMetadata(
            name="max_distance",
            blender_path="field.distance_max",
            prop_type="float",
            default=0.0,
            min_value=0.0,
            description="Maximum influence distance",
        ),
        "use_min_distance": PropertyMetadata(
            name="use_min_distance",
            blender_path="field.use_min_distance",
            prop_type="bool",
            default=False,
            description="Use minimum distance",
        ),
        "min_distance": PropertyMetadata(
            name="min_distance",
            blender_path="field.distance_min",
            prop_type="float",
            default=0.0,
            min_value=0.0,
            description="Minimum influence distance",
        ),
        "flow": PropertyMetadata(
            name="flow",
            blender_path="field.flow",
            prop_type="float",
            default=0.0,
            description="Flow strength for wind",
        ),
        "noise_amount": PropertyMetadata(
            name="noise_amount",
            blender_path="field.noise_amount",
            prop_type="float",
            default=0.0,
            min_value=0.0,
            description="Noise amount for turbulence",
        ),
    },
    readable_properties=(
        "type",
        "strength",
        "falloff_type",
        "falloff_power",
        "use_max_distance",
        "max_distance",
        "use_min_distance",
        "min_distance",
        "flow",
        "noise_amount",
    ),
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

_DECIMATE_METADATA = HandlerMetadata(
    handler_type="DECIMATE",
    category="modifier",
    container_path="",
    properties={
        "decimate_type": PropertyMetadata(
            name="decimate_type",
            blender_path="decimate_type",
            prop_type="enum",
            enum_items=("COLLAPSE", "UNSUBDIV", "DISSOLVE"),
            default="COLLAPSE",
            description="Decimation method",
        ),
        "ratio": PropertyMetadata(
            name="ratio",
            blender_path="ratio",
            prop_type="float",
            default=1.0,
            min_value=0.0,
            max_value=1.0,
            description="Ratio of faces to keep",
        ),
        "use_collapse_triangulate": PropertyMetadata(
            name="use_collapse_triangulate",
            blender_path="use_collapse_triangulate",
            prop_type="bool",
            default=False,
            description="Triangulate during collapse",
        ),
        "vertex_group": PropertyMetadata(
            name="vertex_group",
            blender_path="vertex_group",
            prop_type="string",
            default="",
            description="Vertex group for decimation influence",
        ),
    },
    readable_properties=("decimate_type", "ratio", "use_collapse_triangulate", "vertex_group"),
)

_REMESH_METADATA = HandlerMetadata(
    handler_type="REMESH",
    category="modifier",
    container_path="",
    properties={
        "mode": PropertyMetadata(
            name="mode",
            blender_path="mode",
            prop_type="enum",
            enum_items=("VOXEL", "SHARP", "SMOOTH"),
            default="VOXEL",
            description="Remesh algorithm",
        ),
        "voxel_size": PropertyMetadata(
            name="voxel_size",
            blender_path="voxel_size",
            prop_type="float",
            default=0.1,
            min_value=0.0001,
            description="Voxel size for remeshing",
        ),
        "adaptivity": PropertyMetadata(
            name="adaptivity",
            blender_path="adaptivity",
            prop_type="float",
            default=0.0,
            min_value=0.0,
            max_value=1.0,
            description="Adaptivity of the mesh",
        ),
        "use_smooth_shade": PropertyMetadata(
            name="use_smooth_shade",
            blender_path="use_smooth_shade",
            prop_type="bool",
            default=False,
            description="Use smooth shading",
        ),
        "use_remove_disconnected": PropertyMetadata(
            name="use_remove_disconnected",
            blender_path="use_remove_disconnected",
            prop_type="bool",
            default=True,
            description="Remove disconnected pieces",
        ),
    },
    readable_properties=("mode", "voxel_size", "adaptivity", "use_smooth_shade", "use_remove_disconnected"),
)

_SHRINKWRAP_METADATA = HandlerMetadata(
    handler_type="SHRINKWRAP",
    category="modifier",
    container_path="",
    properties={
        "wrap_method": PropertyMetadata(
            name="wrap_method",
            blender_path="wrap_method",
            prop_type="enum",
            enum_items=("NEAREST_SURFACE", "PROJECT", "NEAREST_VERTEX", "TARGET_PROJECT"),
            default="NEAREST_SURFACE",
            description="Method for shrinkwrap",
        ),
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Object to shrinkwrap to",
        ),
        "offset": PropertyMetadata(
            name="offset",
            blender_path="offset",
            prop_type="float",
            default=0.0,
            description="Distance from target",
        ),
        "use_negative_direction": PropertyMetadata(
            name="use_negative_direction",
            blender_path="use_negative_direction",
            prop_type="bool",
            default=False,
            description="Project in negative direction",
        ),
        "use_positive_direction": PropertyMetadata(
            name="use_positive_direction",
            blender_path="use_positive_direction",
            prop_type="bool",
            default=True,
            description="Project in positive direction",
        ),
        "use_keep_above_surface": PropertyMetadata(
            name="use_keep_above_surface",
            blender_path="use_keep_above_surface",
            prop_type="bool",
            default=False,
            description="Keep vertices above surface",
        ),
    },
    readable_properties=(
        "wrap_method",
        "target",
        "offset",
        "use_negative_direction",
        "use_positive_direction",
        "use_keep_above_surface",
    ),
)

_SKIN_METADATA = HandlerMetadata(
    handler_type="SKIN",
    category="modifier",
    container_path="",
    properties={
        "branch_smoothing": PropertyMetadata(
            name="branch_smoothing",
            blender_path="branch_smoothing",
            prop_type="float",
            default=0.0,
            min_value=0.0,
            max_value=1.0,
            description="Smoothing of branching edges",
        ),
        "use_smooth_shade": PropertyMetadata(
            name="use_smooth_shade",
            blender_path="use_smooth_shade",
            prop_type="bool",
            default=False,
            description="Use smooth shading",
        ),
        "use_x_symmetry": PropertyMetadata(
            name="use_x_symmetry",
            blender_path="use_x_symmetry",
            prop_type="bool",
            default=False,
            description="Symmetry along X axis",
        ),
        "use_y_symmetry": PropertyMetadata(
            name="use_y_symmetry",
            blender_path="use_y_symmetry",
            prop_type="bool",
            default=False,
            description="Symmetry along Y axis",
        ),
        "use_z_symmetry": PropertyMetadata(
            name="use_z_symmetry",
            blender_path="use_z_symmetry",
            prop_type="bool",
            default=False,
            description="Symmetry along Z axis",
        ),
    },
    readable_properties=("branch_smoothing", "use_smooth_shade", "use_x_symmetry", "use_y_symmetry", "use_z_symmetry"),
)

_WIREFRAME_METADATA = HandlerMetadata(
    handler_type="WIREFRAME",
    category="modifier",
    container_path="",
    properties={
        "thickness": PropertyMetadata(
            name="thickness",
            blender_path="thickness",
            prop_type="float",
            default=0.02,
            min_value=0.0,
            description="Wireframe thickness",
        ),
        "offset": PropertyMetadata(
            name="offset",
            blender_path="offset",
            prop_type="float",
            default=1.0,
            min_value=-1.0,
            max_value=1.0,
            description="Offset along normals",
        ),
        "use_boundary": PropertyMetadata(
            name="use_boundary",
            blender_path="use_boundary",
            prop_type="bool",
            default=True,
            description="Fill boundary edges",
        ),
        "use_even_offset": PropertyMetadata(
            name="use_even_offset",
            blender_path="use_even_offset",
            prop_type="bool",
            default=True,
            description="Even offset for thickness",
        ),
        "use_relative_offset": PropertyMetadata(
            name="use_relative_offset",
            blender_path="use_relative_offset",
            prop_type="bool",
            default=False,
            description="Relative thickness",
        ),
        "use_replace": PropertyMetadata(
            name="use_replace",
            blender_path="use_replace",
            prop_type="bool",
            default=True,
            description="Replace original mesh",
        ),
    },
    readable_properties=(
        "thickness",
        "offset",
        "use_boundary",
        "use_even_offset",
        "use_relative_offset",
        "use_replace",
    ),
)

_LATTICE_METADATA = HandlerMetadata(
    handler_type="LATTICE",
    category="modifier",
    container_path="",
    properties={
        "object": PropertyMetadata(
            name="object",
            blender_path="object",
            prop_type="object_ref",
            default=None,
            description="Lattice object to use",
        ),
        "strength": PropertyMetadata(
            name="strength",
            blender_path="strength",
            prop_type="float",
            default=1.0,
            min_value=0.0,
            max_value=1.0,
            description="Strength of lattice deformation",
        ),
        "vertex_group": PropertyMetadata(
            name="vertex_group",
            blender_path="vertex_group",
            prop_type="string",
            default="",
            description="Vertex group for influence",
        ),
    },
    readable_properties=("object", "strength", "vertex_group"),
)

_HOOK_METADATA = HandlerMetadata(
    handler_type="HOOK",
    category="modifier",
    container_path="",
    properties={
        "object": PropertyMetadata(
            name="object",
            blender_path="object",
            prop_type="object_ref",
            default=None,
            description="Object to use as hook target",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "strength": PropertyMetadata(
            name="strength",
            blender_path="strength",
            prop_type="float",
            default=1.0,
            min_value=0.0,
            max_value=1.0,
            description="Hook influence strength",
        ),
        "falloff_type": PropertyMetadata(
            name="falloff_type",
            blender_path="falloff_type",
            prop_type="enum",
            enum_items=("NONE", "CURVE", "SMOOTH", "SPHERE", "ROOT", "INVERSE_SQUARE", "SHARP", "LINEAR"),
            default="SMOOTH",
            description="Falloff type for hook influence",
        ),
        "falloff_radius": PropertyMetadata(
            name="falloff_radius",
            blender_path="falloff_radius",
            prop_type="float",
            default=0.0,
            min_value=0.0,
            description="Radius for falloff",
        ),
    },
    readable_properties=("object", "subtarget", "strength", "falloff_type", "falloff_radius"),
)

# =============================================================================
# Constraint Metadata Definitions
# =============================================================================

_COPY_LOCATION_METADATA = HandlerMetadata(
    handler_type="COPY_LOCATION",
    category="constraint",
    container_path="",
    properties={
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Target object",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "use_x": PropertyMetadata(
            name="use_x",
            blender_path="use_x",
            prop_type="bool",
            default=True,
            description="Copy X location",
        ),
        "use_y": PropertyMetadata(
            name="use_y",
            blender_path="use_y",
            prop_type="bool",
            default=True,
            description="Copy Y location",
        ),
        "use_z": PropertyMetadata(
            name="use_z",
            blender_path="use_z",
            prop_type="bool",
            default=True,
            description="Copy Z location",
        ),
        "use_offset": PropertyMetadata(
            name="use_offset",
            blender_path="use_offset",
            prop_type="bool",
            default=False,
            description="Add offset to location",
        ),
        "invert_x": PropertyMetadata(
            name="invert_x",
            blender_path="invert_x",
            prop_type="bool",
            default=False,
            description="Invert X axis",
        ),
        "invert_y": PropertyMetadata(
            name="invert_y",
            blender_path="invert_y",
            prop_type="bool",
            default=False,
            description="Invert Y axis",
        ),
        "invert_z": PropertyMetadata(
            name="invert_z",
            blender_path="invert_z",
            prop_type="bool",
            default=False,
            description="Invert Z axis",
        ),
    },
    readable_properties=(
        "target",
        "subtarget",
        "use_x",
        "use_y",
        "use_z",
        "use_offset",
        "invert_x",
        "invert_y",
        "invert_z",
    ),
)

_COPY_ROTATION_METADATA = HandlerMetadata(
    handler_type="COPY_ROTATION",
    category="constraint",
    container_path="",
    properties={
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Target object",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "use_x": PropertyMetadata(
            name="use_x",
            blender_path="use_x",
            prop_type="bool",
            default=True,
            description="Copy X rotation",
        ),
        "use_y": PropertyMetadata(
            name="use_y",
            blender_path="use_y",
            prop_type="bool",
            default=True,
            description="Copy Y rotation",
        ),
        "use_z": PropertyMetadata(
            name="use_z",
            blender_path="use_z",
            prop_type="bool",
            default=True,
            description="Copy Z rotation",
        ),
        "euler_order": PropertyMetadata(
            name="euler_order",
            blender_path="euler_order",
            prop_type="enum",
            enum_items=("AUTO", "XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX"),
            default="AUTO",
            description="Euler order for rotation",
        ),
        "mix_mode": PropertyMetadata(
            name="mix_mode",
            blender_path="mix_mode",
            prop_type="enum",
            enum_items=("REPLACE", "BEFORE", "AFTER", "SPLIT_BEFORE", "SPLIT_AFTER"),
            default="REPLACE",
            description="How to combine rotations",
        ),
    },
    readable_properties=("target", "subtarget", "use_x", "use_y", "use_z", "euler_order", "mix_mode"),
)

_COPY_SCALE_METADATA = HandlerMetadata(
    handler_type="COPY_SCALE",
    category="constraint",
    container_path="",
    properties={
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Target object",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "use_x": PropertyMetadata(
            name="use_x",
            blender_path="use_x",
            prop_type="bool",
            default=True,
            description="Copy X scale",
        ),
        "use_y": PropertyMetadata(
            name="use_y",
            blender_path="use_y",
            prop_type="bool",
            default=True,
            description="Copy Y scale",
        ),
        "use_z": PropertyMetadata(
            name="use_z",
            blender_path="use_z",
            prop_type="bool",
            default=True,
            description="Copy Z scale",
        ),
        "power": PropertyMetadata(
            name="power",
            blender_path="power",
            prop_type="float",
            default=1.0,
            min_value=0.0,
            description="Power of scale interpolation",
        ),
    },
    readable_properties=("target", "subtarget", "use_x", "use_y", "use_z", "power"),
)

_TRACK_TO_METADATA = HandlerMetadata(
    handler_type="TRACK_TO",
    category="constraint",
    container_path="",
    properties={
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Target object to track",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "track_axis": PropertyMetadata(
            name="track_axis",
            blender_path="track_axis",
            prop_type="enum",
            enum_items=("TRACK_X", "TRACK_Y", "TRACK_Z", "TRACK_NEGATIVE_X", "TRACK_NEGATIVE_Y", "TRACK_NEGATIVE_Z"),
            default="TRACK_NEGATIVE_Z",
            description="Axis that points to target",
        ),
        "up_axis": PropertyMetadata(
            name="up_axis",
            blender_path="up_axis",
            prop_type="enum",
            enum_items=("UP_X", "UP_Y", "UP_Z"),
            default="UP_Y",
            description="Axis that points upward",
        ),
        "use_target_z": PropertyMetadata(
            name="use_target_z",
            blender_path="use_target_z",
            prop_type="bool",
            default=False,
            description="Use target Z axis",
        ),
    },
    readable_properties=("target", "subtarget", "track_axis", "up_axis", "use_target_z"),
)

_DAMPED_TRACK_METADATA = HandlerMetadata(
    handler_type="DAMPED_TRACK",
    category="constraint",
    container_path="",
    properties={
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Target object to track",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "track_axis": PropertyMetadata(
            name="track_axis",
            blender_path="track_axis",
            prop_type="enum",
            enum_items=("TRACK_X", "TRACK_Y", "TRACK_Z", "TRACK_NEGATIVE_X", "TRACK_NEGATIVE_Y", "TRACK_NEGATIVE_Z"),
            default="TRACK_Z",
            description="Axis that points to target",
        ),
        "influence": PropertyMetadata(
            name="influence",
            blender_path="influence",
            prop_type="float",
            default=1.0,
            min_value=0.0,
            max_value=1.0,
            description="Influence of the constraint",
        ),
    },
    readable_properties=("target", "subtarget", "track_axis", "influence"),
)

_LOCKED_TRACK_METADATA = HandlerMetadata(
    handler_type="LOCKED_TRACK",
    category="constraint",
    container_path="",
    properties={
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Target object to track",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "track_axis": PropertyMetadata(
            name="track_axis",
            blender_path="track_axis",
            prop_type="enum",
            enum_items=("TRACK_X", "TRACK_Y", "TRACK_Z", "TRACK_NEGATIVE_X", "TRACK_NEGATIVE_Y", "TRACK_NEGATIVE_Z"),
            default="TRACK_Z",
            description="Axis that points to target",
        ),
        "lock_axis": PropertyMetadata(
            name="lock_axis",
            blender_path="lock_axis",
            prop_type="enum",
            enum_items=("LOCK_X", "LOCK_Y", "LOCK_Z"),
            default="LOCK_Z",
            description="Locked axis",
        ),
    },
    readable_properties=("target", "subtarget", "track_axis", "lock_axis"),
)

_IK_METADATA = HandlerMetadata(
    handler_type="IK",
    category="constraint",
    container_path="",
    properties={
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Target object for IK",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "pole_target": PropertyMetadata(
            name="pole_target",
            blender_path="pole_target",
            prop_type="object_ref",
            default=None,
            description="Pole target object",
        ),
        "pole_subtarget": PropertyMetadata(
            name="pole_subtarget",
            blender_path="pole_subtarget",
            prop_type="string",
            default="",
            description="Bone for pole target",
        ),
        "pole_angle": PropertyMetadata(
            name="pole_angle",
            blender_path="pole_angle",
            prop_type="float",
            default=0.0,
            description="Pole angle in radians",
        ),
        "chain_count": PropertyMetadata(
            name="chain_count",
            blender_path="chain_count",
            prop_type="int",
            default=2,
            min_value=1,
            description="Number of bones in IK chain",
        ),
        "use_tail": PropertyMetadata(
            name="use_tail",
            blender_path="use_tail",
            prop_type="bool",
            default=False,
            description="Include tail bone in chain",
        ),
        "use_stretch": PropertyMetadata(
            name="use_stretch",
            blender_path="use_stretch",
            prop_type="bool",
            default=True,
            description="Allow bone stretching",
        ),
        "iterations": PropertyMetadata(
            name="iterations",
            blender_path="iterations",
            prop_type="int",
            default=500,
            min_value=0,
            description="IK solver iterations",
        ),
    },
    readable_properties=(
        "target",
        "subtarget",
        "pole_target",
        "pole_subtarget",
        "pole_angle",
        "chain_count",
        "use_tail",
        "use_stretch",
        "iterations",
    ),
)

_STRETCH_TO_METADATA = HandlerMetadata(
    handler_type="STRETCH_TO",
    category="constraint",
    container_path="",
    properties={
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Target object",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "rest_length": PropertyMetadata(
            name="rest_length",
            blender_path="rest_length",
            prop_type="float",
            default=0.0,
            min_value=0.0,
            description="Rest length of bone",
        ),
        "bulge": PropertyMetadata(
            name="bulge",
            blender_path="bulge",
            prop_type="float",
            default=1.0,
            min_value=0.0,
            description="Bulge factor",
        ),
        "volume": PropertyMetadata(
            name="volume",
            blender_path="volume",
            prop_type="enum",
            enum_items=("VOLUME_XZ", "VOLUME_X", "VOLUME_Z", "NO_VOLUME"),
            default="VOLUME_XZ",
            description="Volume preservation mode",
        ),
        "keep_axis": PropertyMetadata(
            name="keep_axis",
            blender_path="keep_axis",
            prop_type="enum",
            enum_items=("PLANE_X", "PLANE_Z", "SWING_Y"),
            default="PLANE_X",
            description="Axis to maintain",
        ),
    },
    readable_properties=("target", "subtarget", "rest_length", "bulge", "volume", "keep_axis"),
)

_LIMIT_DISTANCE_METADATA = HandlerMetadata(
    handler_type="LIMIT_DISTANCE",
    category="constraint",
    container_path="",
    properties={
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Target object",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "distance": PropertyMetadata(
            name="distance",
            blender_path="distance",
            prop_type="float",
            default=1.0,
            min_value=0.0,
            description="Distance limit",
        ),
        "limit_mode": PropertyMetadata(
            name="limit_mode",
            blender_path="limit_mode",
            prop_type="enum",
            enum_items=("LIMITDIST_INSIDE", "LIMITDIST_OUTSIDE", "LIMITDIST_ONSURFACE"),
            default="LIMITDIST_INSIDE",
            description="Distance limit mode",
        ),
        "use_transform_limit": PropertyMetadata(
            name="use_transform_limit",
            blender_path="use_transform_limit",
            prop_type="bool",
            default=True,
            description="Use for transform limit",
        ),
    },
    readable_properties=("target", "subtarget", "distance", "limit_mode", "use_transform_limit"),
)

_FLOOR_METADATA = HandlerMetadata(
    handler_type="FLOOR",
    category="constraint",
    container_path="",
    properties={
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Target object",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "floor_location": PropertyMetadata(
            name="floor_location",
            blender_path="floor_location",
            prop_type="enum",
            enum_items=("FLOOR_X", "FLOOR_Y", "FLOOR_Z", "FLOOR_NEGATIVE_X", "FLOOR_NEGATIVE_Y", "FLOOR_NEGATIVE_Z"),
            default="FLOOR_Z",
            description="Floor axis",
        ),
        "use_sticky": PropertyMetadata(
            name="use_sticky",
            blender_path="use_sticky",
            prop_type="bool",
            default=False,
            description="Stick to floor",
        ),
        "offset": PropertyMetadata(
            name="offset",
            blender_path="offset",
            prop_type="float",
            default=0.0,
            description="Offset from floor",
        ),
    },
    readable_properties=("target", "subtarget", "floor_location", "use_sticky", "offset"),
)

_CHILD_OF_METADATA = HandlerMetadata(
    handler_type="CHILD_OF",
    category="constraint",
    container_path="",
    properties={
        "target": PropertyMetadata(
            name="target",
            blender_path="target",
            prop_type="object_ref",
            default=None,
            description="Target object",
        ),
        "subtarget": PropertyMetadata(
            name="subtarget",
            blender_path="subtarget",
            prop_type="string",
            default="",
            description="Bone name if target is armature",
        ),
        "use_location_x": PropertyMetadata(
            name="use_location_x",
            blender_path="use_location_x",
            prop_type="bool",
            default=True,
            description="Inherit X location",
        ),
        "use_location_y": PropertyMetadata(
            name="use_location_y",
            blender_path="use_location_y",
            prop_type="bool",
            default=True,
            description="Inherit Y location",
        ),
        "use_location_z": PropertyMetadata(
            name="use_location_z",
            blender_path="use_location_z",
            prop_type="bool",
            default=True,
            description="Inherit Z location",
        ),
        "use_rotation_x": PropertyMetadata(
            name="use_rotation_x",
            blender_path="use_rotation_x",
            prop_type="bool",
            default=True,
            description="Inherit X rotation",
        ),
        "use_rotation_y": PropertyMetadata(
            name="use_rotation_y",
            blender_path="use_rotation_y",
            prop_type="bool",
            default=True,
            description="Inherit Y rotation",
        ),
        "use_rotation_z": PropertyMetadata(
            name="use_rotation_z",
            blender_path="use_rotation_z",
            prop_type="bool",
            default=True,
            description="Inherit Z rotation",
        ),
        "use_scale_x": PropertyMetadata(
            name="use_scale_x",
            blender_path="use_scale_x",
            prop_type="bool",
            default=True,
            description="Inherit X scale",
        ),
        "use_scale_y": PropertyMetadata(
            name="use_scale_y",
            blender_path="use_scale_y",
            prop_type="bool",
            default=True,
            description="Inherit Y scale",
        ),
        "use_scale_z": PropertyMetadata(
            name="use_scale_z",
            blender_path="use_scale_z",
            prop_type="bool",
            default=True,
            description="Inherit Z scale",
        ),
    },
    readable_properties=(
        "target",
        "subtarget",
        "use_location_x",
        "use_location_y",
        "use_location_z",
        "use_rotation_x",
        "use_rotation_y",
        "use_rotation_z",
        "use_scale_x",
        "use_scale_y",
        "use_scale_z",
    ),
)


# Register all built-in metadata
def _register_builtins() -> None:
    """Register all built-in handler metadata."""
    # Physics modifiers
    register_handler_metadata(_CLOTH_METADATA)
    register_handler_metadata(_SOFT_BODY_METADATA)
    register_handler_metadata(_FLUID_METADATA)
    register_handler_metadata(_WAVE_METADATA)
    register_handler_metadata(_RIGID_BODY_METADATA)
    register_handler_metadata(_PARTICLE_METADATA)
    register_handler_metadata(_FORCE_FIELD_METADATA)
    # Mesh modifiers
    register_handler_metadata(_MIRROR_METADATA)
    register_handler_metadata(_SUBSURF_METADATA)
    register_handler_metadata(_ARRAY_METADATA)
    register_handler_metadata(_BOOLEAN_METADATA)
    register_handler_metadata(_SOLIDIFY_METADATA)
    register_handler_metadata(_BEVEL_METADATA)
    register_handler_metadata(_DECIMATE_METADATA)
    register_handler_metadata(_REMESH_METADATA)
    register_handler_metadata(_SHRINKWRAP_METADATA)
    register_handler_metadata(_SKIN_METADATA)
    register_handler_metadata(_WIREFRAME_METADATA)
    register_handler_metadata(_LATTICE_METADATA)
    register_handler_metadata(_HOOK_METADATA)
    # Constraints
    register_handler_metadata(_COPY_LOCATION_METADATA)
    register_handler_metadata(_COPY_ROTATION_METADATA)
    register_handler_metadata(_COPY_SCALE_METADATA)
    register_handler_metadata(_TRACK_TO_METADATA)
    register_handler_metadata(_DAMPED_TRACK_METADATA)
    register_handler_metadata(_LOCKED_TRACK_METADATA)
    register_handler_metadata(_IK_METADATA)
    register_handler_metadata(_STRETCH_TO_METADATA)
    register_handler_metadata(_LIMIT_DISTANCE_METADATA)
    register_handler_metadata(_FLOOR_METADATA)
    register_handler_metadata(_CHILD_OF_METADATA)


# Auto-register on module import
_register_builtins()
