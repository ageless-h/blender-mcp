# -*- coding: utf-8 -*-
"""Shared utility functions for handler implementations."""

from __future__ import annotations

from typing import Any


def create_mesh_primitive(mesh: Any, primitive: str, params: dict[str, Any]) -> None:
    """Create primitive geometry on a mesh data block using bmesh.

    Args:
        mesh: The bpy.types.Mesh to fill with geometry
        primitive: Primitive type (cube, sphere, cylinder, cone, plane, icosphere, torus)
        params: Additional parameters (size, radius, depth, segments, etc.)

    Raises:
        ValueError: If the primitive type is unknown
    """
    import bmesh  # type: ignore

    bm = bmesh.new()
    try:
        kind = primitive.lower()
        size = params.get("size", 2.0)

        if kind == "cube":
            bmesh.ops.create_cube(bm, size=size)
        elif kind == "sphere":
            segments = params.get("segments", 32)
            ring_count = params.get("ring_count", 16)
            radius = params.get("radius", size / 2)
            bmesh.ops.create_uvsphere(
                bm, u_segments=segments, v_segments=ring_count, radius=radius
            )
        elif kind == "cylinder":
            segments = params.get("segments", 32)
            depth = params.get("depth", 2.0)
            radius = params.get("radius", size / 2)
            bmesh.ops.create_cone(
                bm,
                cap_ends=True,
                cap_tris=False,
                segments=segments,
                radius1=radius,
                radius2=radius,
                depth=depth,
            )
        elif kind == "cone":
            segments = params.get("segments", 32)
            depth = params.get("depth", 2.0)
            radius = params.get("radius", size / 2)
            bmesh.ops.create_cone(
                bm,
                cap_ends=True,
                cap_tris=False,
                segments=segments,
                radius1=radius,
                radius2=0,
                depth=depth,
            )
        elif kind == "plane":
            bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size)
        elif kind == "icosphere":
            subdivisions = params.get("subdivisions", 2)
            radius = params.get("radius", size / 2)
            bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius)
        elif kind == "torus":
            import bpy  # type: ignore

            major_radius = params.get("major_radius", 1.0)
            minor_radius = params.get("minor_radius", 0.25)
            major_segments = params.get("major_segments", 48)
            minor_segments = params.get("minor_segments", 12)
            location = params.get("_location", (0, 0, 0))
            try:
                bmesh.ops.create_torus(
                    bm,
                    major_segments=major_segments,
                    minor_segments=minor_segments,
                    major_radius=major_radius,
                    minor_radius=minor_radius,
                )
            except AttributeError:
                bm.free()
                result = bpy.ops.mesh.primitive_torus_add(
                    major_segments=major_segments,
                    minor_segments=minor_segments,
                    major_radius=major_radius,
                    minor_radius=minor_radius,
                    location=location,
                )
                if result == {"FINISHED"} and bpy.context.active_object:
                    obj = bpy.context.active_object
                    if obj.data and obj.data != mesh:
                        bm2 = bmesh.new()
                        bm2.from_mesh(obj.data)
                        bm2.to_mesh(mesh)
                        bm2.free()
                        mesh.validate()
                        mesh.update(calc_edges=True, calc_edges_loose=True)
                        bpy.data.objects.remove(obj, do_unlink=True)
                    return
                raise
        else:
            raise ValueError(f"Unknown primitive type: {primitive}")

        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.validate()
    mesh.update(calc_edges=True, calc_edges_loose=True)


def link_data_to_scene(data_block: Any, params: dict[str, Any]) -> Any:
    """Create a Blender object from a data block and link it to the scene.

    Args:
        data_block: The bpy data block (camera, light, curve, etc.)
        params: Parameters dict, reads:
            - object_name: Name for the object (default: data_block.name)
            - collection: Target collection name (default: scene collection)
            - location: [x, y, z] position
            - rotation: [x, y, z] euler rotation

    Returns:
        The created bpy.types.Object instance
    """
    import bpy  # type: ignore

    obj_name = params.get("object_name", data_block.name)
    obj = bpy.data.objects.new(obj_name, data_block)
    collection_name = params.get("collection")
    if collection_name and collection_name in bpy.data.collections:
        bpy.data.collections[collection_name].objects.link(obj)
    else:
        bpy.context.scene.collection.objects.link(obj)
    if "location" in params:
        obj.location = tuple(params["location"])
    if "rotation" in params:
        obj.rotation_euler = tuple(params["rotation"])
    return obj


def find_referencing_objects(data_block: Any, object_type: str) -> dict[str, list[str]]:
    """Find all objects that reference a given data block.

    Scans bpy.data.objects for objects of the specified type whose .data
    attribute points to the given data block. Also collects the collection
    names those objects belong to.

    Args:
        data_block: The bpy data block to search for references to
        object_type: Blender object type string (e.g., "CAMERA", "LIGHT")

    Returns:
        Dict with "objects" (list of object names) and "collections"
        (deduplicated list of collection names)
    """
    import bpy  # type: ignore

    objects = [
        obj.name
        for obj in bpy.data.objects
        if obj.type == object_type and obj.data == data_block
    ]
    collections: list[str] = []
    if objects:
        for coll in bpy.data.collections:
            if any(obj_name in coll.objects for obj_name in objects):
                if coll.name not in collections:
                    collections.append(coll.name)
    return {"objects": objects, "collections": collections}
