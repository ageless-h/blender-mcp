# -*- coding: utf-8 -*-
"""UV mapping handler — seams, unwrap algorithms, pack, UV layers."""
from __future__ import annotations

import logging
from typing import Any

from ..response import _ok, _error, check_bpy_available, bpy_unavailable_error

logger = logging.getLogger(__name__)


def uv_manage(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Manage UV mapping operations."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    action = payload.get("action", "")
    object_name = payload.get("object_name", "")

    if not action:
        return _error(code="invalid_params", message="action is required", started=started)
    if not object_name:
        return _error(code="invalid_params", message="object_name is required", started=started)

    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return _error(code="not_found", message=f"Object '{object_name}' not found", started=started)
    if obj.type != "MESH":
        return _error(code="invalid_params", message=f"Object '{object_name}' is not a mesh", started=started)

    try:
        # UV layer management (no mode switch needed)
        if action == "add_uv_map":
            uv_name = payload.get("uv_map_name", "UVMap")
            obj.data.uv_layers.new(name=uv_name)
            return _ok(result={"action": action, "uv_map": uv_name}, started=started)

        if action == "remove_uv_map":
            uv_name = payload.get("uv_map_name", "")
            uv_layer = obj.data.uv_layers.get(uv_name)
            if not uv_layer:
                return _error(code="not_found", message=f"UV map '{uv_name}' not found", started=started)
            obj.data.uv_layers.remove(uv_layer)
            return _ok(result={"action": action, "removed": uv_name}, started=started)

        if action == "set_active_uv":
            uv_name = payload.get("uv_map_name", "")
            uv_layer = obj.data.uv_layers.get(uv_name)
            if not uv_layer:
                return _error(code="not_found", message=f"UV map '{uv_name}' not found", started=started)
            obj.data.uv_layers.active = uv_layer
            return _ok(result={"action": action, "active": uv_name}, started=started)

        # Operations requiring edit mode
        original_mode = obj.mode if hasattr(obj, "mode") else "OBJECT"
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        if original_mode != "EDIT":
            with bpy.context.temp_override(active_object=obj, object=obj, selected_objects=[obj]):
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action="SELECT")

        try:
            if action == "mark_seam":
                bpy.ops.mesh.mark_seam(clear=False)
                result_msg = "Seams marked on selected edges"
            elif action == "clear_seam":
                bpy.ops.mesh.mark_seam(clear=True)
                result_msg = "Seams cleared on selected edges"
            elif action == "unwrap":
                bpy.ops.uv.unwrap()
                result_msg = "UV unwrap completed"
            elif action == "smart_project":
                angle = payload.get("angle_limit", 66.0)
                margin = payload.get("island_margin", 0.02)
                correct = payload.get("correct_aspect", True)
                bpy.ops.uv.smart_project(
                    angle_limit=angle * 3.14159 / 180.0,
                    island_margin=margin,
                    correct_aspect=correct,
                )
                result_msg = f"Smart UV project completed (angle={angle}°, margin={margin})"
            elif action == "cube_project":
                bpy.ops.uv.cube_project()
                result_msg = "Cube projection completed"
            elif action == "cylinder_project":
                correct = payload.get("correct_aspect", True)
                bpy.ops.uv.cylinder_project(correct_aspect=correct)
                result_msg = "Cylinder projection completed"
            elif action == "sphere_project":
                correct = payload.get("correct_aspect", True)
                bpy.ops.uv.sphere_project(correct_aspect=correct)
                result_msg = "Sphere projection completed"
            elif action == "lightmap_pack":
                bpy.ops.uv.lightmap_pack()
                result_msg = "Lightmap pack completed"
            elif action == "pack_islands":
                margin = payload.get("island_margin", 0.02)
                bpy.ops.uv.pack_islands(margin=margin)
                result_msg = f"UV islands packed (margin={margin})"
            elif action == "average_island_scale":
                bpy.ops.uv.average_islands_scale()
                result_msg = "UV island scales averaged"
            else:
                return _error(code="invalid_params", message=f"Unknown UV action: {action}", started=started)
        finally:
            if original_mode != "EDIT":
                with bpy.context.temp_override(active_object=obj, object=obj, selected_objects=[obj]):
                    bpy.ops.object.mode_set(mode=original_mode)

        return _ok(result={"action": action, "object": object_name, "message": result_msg}, started=started)

    except Exception as exc:
        return _error(code="operation_failed", message=f"UV {action} failed: {exc}", started=started)
