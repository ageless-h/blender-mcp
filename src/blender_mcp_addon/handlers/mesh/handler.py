# -*- coding: utf-8 -*-
"""Mesh editing handler — extrude, inset, bevel, loop cut, dissolve, merge, etc."""

from __future__ import annotations

import logging
from typing import Any

from ..context_utils import get_view3d_override
from ..error_codes import ErrorCode
from ..response import _error, _ok, bpy_unavailable_error, check_bpy_available

logger = logging.getLogger(__name__)


def edit_mesh(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Edit mesh geometry using various operations.

    Args:
        payload: Mesh edit parameters:
            - object_name: Name of the mesh object (required)
            - action: Operation to perform (required):
                - extrude: Extrude selected geometry
                - extrude_individual: Extrude each face individually
                - inset: Inset selected faces
                - bevel: Bevel selected edges/vertices
                - loop_cut: Add loop cut
                - dissolve_vertices: Dissolve selected vertices
                - dissolve_edges: Dissolve selected edges
                - dissolve_faces: Dissolve selected faces
                - merge_vertices: Merge selected vertices by distance
                - subdivide: Subdivide selected edges/faces
                - delete: Delete selected geometry
                - select_all: Select/deselect all
                - select_mode: Set selection mode (VERT/EDGE/FACE)
            - selection: Selection mode for delete action (VERT/EDGE/FACE)
            - dissolve_verts: For dissolve_edges, also dissolve interior vertices
            - threshold: Merge threshold for merge_vertices
            - segments: Number of segments for bevel/subdivide/loop_cut
            - amount: Amount for inset/bevel
            - use_boundary: For inset, inset boundary edges
            - use_even_offset: For inset, use even offset
            - use_relative_offset: For inset, use relative offset
            - use_interpolate: For bevel, use interpolate
            - number_cuts: For loop_cut, number of cuts
            - quad_corner_type: For loop_cut, corner type

    Returns:
        Dict with operation result info
    """
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    action = payload.get("action", "")
    object_name = payload.get("object_name", "")

    if not action:
        return _error(code=ErrorCode.INVALID_PARAMS, message="action is required", started=started)
    if not object_name:
        return _error(code=ErrorCode.INVALID_PARAMS, message="object_name is required", started=started)

    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return _error(code=ErrorCode.NOT_FOUND, message=f"Object '{object_name}' not found", started=started)
    if obj.type != "MESH":
        return _error(code=ErrorCode.INVALID_PARAMS, message=f"Object '{object_name}' is not a mesh", started=started)

    try:
        original_mode = obj.mode if hasattr(obj, "mode") else "OBJECT"
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        ctx = get_view3d_override(bpy, obj)

        if original_mode != "EDIT":
            with bpy.context.temp_override(**ctx):
                bpy.ops.object.mode_set(mode="EDIT")

        try:
            with bpy.context.temp_override(**ctx):
                if action == "select_all":
                    sel_action = payload.get("select_action", "SELECT")
                    bpy.ops.mesh.select_all(action=sel_action)
                    result_msg = f"Select all: {sel_action}"

                elif action == "select_mode":
                    mode = payload.get("mode", "FACE")
                    if mode == "VERT":
                        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="VERT")
                    elif mode == "EDGE":
                        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="EDGE")
                    else:
                        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type="FACE")
                    result_msg = f"Selection mode: {mode}"

                elif action == "extrude":
                    bpy.ops.mesh.extrude_region_move(
                        MESH_OT_extrude_region={"mirror": False},
                        TRANSFORM_OT_translate={"value": (0, 0, 0)},
                    )
                    result_msg = "Extruded selected geometry"

                elif action == "extrude_individual":
                    bpy.ops.mesh.extrude_faces_move(
                        MESH_OT_extrude_faces_ind={"mirror": False},
                        TRANSFORM_OT_shrink_fatten={"value": 0},
                    )
                    result_msg = "Extruded faces individually"

                elif action == "inset":
                    amount = payload.get("amount", 0.0)
                    use_boundary = payload.get("use_boundary", True)
                    use_even_offset = payload.get("use_even_offset", True)
                    use_relative_offset = payload.get("use_relative_offset", False)
                    bpy.ops.mesh.inset(
                        thickness=amount,
                        use_boundary=use_boundary,
                        use_even_offset=use_even_offset,
                        use_relative_offset=use_relative_offset,
                    )
                    result_msg = f"Inset faces (amount={amount})"

                elif action == "bevel":
                    segments = payload.get("segments", 2)
                    amount = payload.get("amount", 0.1)
                    bpy.ops.mesh.bevel(
                        segments=segments,
                        width=amount,
                    )
                    result_msg = f"Bevel (segments={segments}, amount={amount})"

                elif action == "loop_cut":
                    number_cuts = payload.get("number_cuts", 1)
                    bpy.ops.mesh.loopcut_slide(
                        MESH_OT_loopcut={"number_cuts": number_cuts},
                        TRANSFORM_OT_edge_slide={"value": 0.5},
                    )
                    result_msg = f"Loop cut (cuts={number_cuts})"

                elif action == "dissolve_vertices":
                    use_verts = payload.get("use_verts", True)
                    bpy.ops.mesh.dissolve_verts(use_verts=use_verts)
                    result_msg = "Dissolved vertices"

                elif action == "dissolve_edges":
                    use_verts = payload.get("use_verts", False)
                    use_face_split = payload.get("use_face_split", True)
                    bpy.ops.mesh.dissolve_edges(use_verts=use_verts, use_face_split=use_face_split)
                    result_msg = "Dissolved edges"

                elif action == "dissolve_faces":
                    use_verts = payload.get("use_verts", False)
                    bpy.ops.mesh.dissolve_faces(use_verts=use_verts)
                    result_msg = "Dissolved faces"

                elif action == "merge_vertices":
                    threshold = payload.get("threshold", 0.0001)
                    bpy.ops.mesh.remove_doubles(threshold=threshold)
                    result_msg = f"Merged vertices (threshold={threshold})"

                elif action == "subdivide":
                    number_cuts = payload.get("number_cuts", 1)
                    bpy.ops.mesh.subdivide(number_cuts=number_cuts)
                    result_msg = f"Subdivided (cuts={number_cuts})"

                elif action == "delete":
                    selection = payload.get("selection", "FACE")
                    if selection == "VERT":
                        bpy.ops.mesh.delete(type="VERT")
                    elif selection == "EDGE":
                        bpy.ops.mesh.delete(type="EDGE")
                    elif selection == "FACE":
                        bpy.ops.mesh.delete(type="FACE")
                    elif selection == "ONLY_FACE":
                        bpy.ops.mesh.delete(type="ONLY_FACE")
                    else:
                        bpy.ops.mesh.delete(type="ALL")
                    result_msg = f"Deleted {selection}"

                else:
                    return _error(
                        code=ErrorCode.INVALID_PARAMS, message=f"Unknown mesh action: {action}", started=started
                    )
        finally:
            if original_mode != "EDIT":
                with bpy.context.temp_override(**ctx):
                    bpy.ops.object.mode_set(mode=original_mode)

        return _ok(result={"action": action, "object": object_name, "message": result_msg}, started=started)

    except (AttributeError, RuntimeError, TypeError) as exc:
        return _error(code=ErrorCode.OPERATION_FAILED, message=f"Mesh {action} failed: {exc}", started=started)
