# -*- coding: utf-8 -*-
"""DataType enumeration for unified handler system."""

from __future__ import annotations

from enum import Enum


class DataType(str, Enum):
    """Enumeration of all supported Blender data block types.

    Includes:
    - Core object types (object, mesh, curve, etc.)
    - Appearance types (material, texture, image, etc.)
    - Light and camera types
    - Node system types
    - Organization types (collection, scene, workspace)
    - Animation types
    - Physics types
    - Special geometry types
    - Tool types
    - External data types
    - Pseudo-types (context, preferences)
    - Attached types (modifier, constraint, driver, nla_track)
    """

    # Core object types
    OBJECT = "object"
    MESH = "mesh"
    CURVE = "curve"
    SURFACE = "surface"
    METABALL = "metaball"
    ARMATURE = "armature"
    LATTICE = "lattice"

    # Appearance types
    MATERIAL = "material"
    TEXTURE = "texture"
    IMAGE = "image"
    WORLD = "world"
    LINESTYLE = "linestyle"

    # Light and camera types
    CAMERA = "camera"
    LIGHT = "light"
    PROBE = "probe"

    # Node system types
    NODE_TREE = "node_tree"

    # Organization types
    COLLECTION = "collection"
    SCENE = "scene"
    WORKSPACE = "workspace"

    # Animation types
    ACTION = "action"
    KEY = "key"

    # 2D animation types
    GREASE_PENCIL = "grease_pencil"
    ANNOTATION = "annotation"

    # Audio/video types
    SOUND = "sound"
    SPEAKER = "speaker"
    MOVIECLIP = "movieclip"
    MASK = "mask"

    # Physics types
    PARTICLE = "particle"

    # Special geometry types
    VOLUME = "volume"
    POINTCLOUD = "pointcloud"
    HAIR_CURVES = "hair_curves"
    CURVES_NEW = "curves_new"

    # Tool types
    BRUSH = "brush"
    PALETTE = "palette"
    PAINTCURVE = "paintcurve"
    TEXT = "text"
    FONT = "font"

    # External data types
    LIBRARY = "library"
    CACHE_FILE = "cache_file"

    # Pseudo-types (non-data-block entities)
    CONTEXT = "context"
    PREFERENCES = "preferences"

    # Attached types (require parent reference)
    MODIFIER = "modifier"
    CONSTRAINT = "constraint"
    DRIVER = "driver"
    NLA_TRACK = "nla_track"


# Mapping from DataType to bpy.data collection name
DATA_TYPE_TO_COLLECTION: dict[DataType, str] = {
    DataType.OBJECT: "objects",
    DataType.MESH: "meshes",
    DataType.CURVE: "curves",
    DataType.SURFACE: "surfaces",
    DataType.METABALL: "metaballs",
    DataType.ARMATURE: "armatures",
    DataType.LATTICE: "lattices",
    DataType.MATERIAL: "materials",
    DataType.TEXTURE: "textures",
    DataType.IMAGE: "images",
    DataType.WORLD: "worlds",
    DataType.LINESTYLE: "linestyles",
    DataType.CAMERA: "cameras",
    DataType.LIGHT: "lights",
    DataType.PROBE: "lightprobes",
    DataType.NODE_TREE: "node_groups",
    DataType.COLLECTION: "collections",
    DataType.SCENE: "scenes",
    DataType.WORKSPACE: "workspaces",
    DataType.ACTION: "actions",
    DataType.KEY: "shape_keys",
    DataType.GREASE_PENCIL: "grease_pencils",
    DataType.ANNOTATION: "annotations",
    DataType.SOUND: "sounds",
    DataType.SPEAKER: "speakers",
    DataType.MOVIECLIP: "movieclips",
    DataType.MASK: "masks",
    DataType.PARTICLE: "particles",
    DataType.VOLUME: "volumes",
    DataType.POINTCLOUD: "pointclouds",
    DataType.HAIR_CURVES: "hair_curves",
    DataType.CURVES_NEW: "curves",
    DataType.BRUSH: "brushes",
    DataType.PALETTE: "palettes",
    DataType.PAINTCURVE: "paint_curves",
    DataType.TEXT: "texts",
    DataType.FONT: "fonts",
    DataType.LIBRARY: "libraries",
    DataType.CACHE_FILE: "cache_files",
}

# Pseudo-types that don't map to bpy.data collections
PSEUDO_TYPES: set[DataType] = {
    DataType.CONTEXT,
    DataType.PREFERENCES,
}

# Attached types that require a parent reference
ATTACHED_TYPES: set[DataType] = {
    DataType.MODIFIER,
    DataType.CONSTRAINT,
    DataType.DRIVER,
    DataType.NLA_TRACK,
    DataType.KEY,
    DataType.ANNOTATION,
    DataType.CURVES_NEW,
}


def get_collection_name(data_type: DataType) -> str | None:
    """Get the bpy.data collection name for a DataType."""
    return DATA_TYPE_TO_COLLECTION.get(data_type)


def is_pseudo_type(data_type: DataType) -> bool:
    """Check if a DataType is a pseudo-type (not a bpy.data collection)."""
    return data_type in PSEUDO_TYPES


def is_attached_type(data_type: DataType) -> bool:
    """Check if a DataType is an attached type (requires parent reference)."""
    return data_type in ATTACHED_TYPES
