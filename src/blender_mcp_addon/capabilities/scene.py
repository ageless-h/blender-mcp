# -*- coding: utf-8 -*-
"""Scene capability handlers."""
from __future__ import annotations

import logging
from typing import Any

from ..handlers.response import (
    _error,
    _ok,
    bpy_unavailable_error,
    check_bpy_available,
    invalid_params_error,
)

logger = logging.getLogger(__name__)


def scene_read(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Read current scene information."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    try:
        scene = bpy.context.scene
        selected = getattr(bpy.context, "selected_objects", []) or []
        active_obj = getattr(bpy.context, "active_object", None)
        snapshot = {
            "scene_name": getattr(scene, "name", None),
            "object_count": len(getattr(scene, "objects", []) or []),
            "selected_objects": sorted(
                [getattr(obj, "name", "") for obj in selected if getattr(obj, "name", "")]
            ),
            "active_object": getattr(active_obj, "name", None),
        }
        return _ok(result=snapshot, started=started)
    except Exception as exc:
        return _error(
            code="operation_failed",
            message="scene.read failed",
            data={"type": type(exc).__name__},
            started=started,
        )


def scene_write(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Write to the scene (create objects)."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    name = payload.get("name")
    if name is None:
        name = "MCP_POC_CUBE"
    if not isinstance(name, str) or not name.strip():
        return invalid_params_error("'name' must be a non-empty string", started, {"name": name})

    cleanup = payload.get("cleanup")
    if cleanup is None:
        cleanup = True
    if not isinstance(cleanup, bool):
        return invalid_params_error("'cleanup' must be a bool", started, {"cleanup": cleanup})

    try:
        mesh_name = f"{name}_mesh"

        if name in bpy.data.objects:
            existing = bpy.data.objects[name]
            bpy.data.objects.remove(existing, do_unlink=True)
        if mesh_name in bpy.data.meshes:
            existing_mesh = bpy.data.meshes[mesh_name]
            bpy.data.meshes.remove(existing_mesh)

        mesh = bpy.data.meshes.new(name=mesh_name)
        try:
            import bmesh  # type: ignore

            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=2.0)
            bm.to_mesh(mesh)
            bm.free()
        except Exception as exc:
            logger.debug("bmesh cube creation failed, using empty mesh: %s", exc)

        obj = bpy.data.objects.new(name=name, object_data=mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = (0.0, 0.0, 0.0)

        created = True
        if cleanup:
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.meshes.remove(mesh)
        result = {
            "action": "create_cube_placeholder",
            "name": name,
            "created": created,
            "cleanup": cleanup,
        }
        return _ok(result=result, started=started)
    except Exception as exc:
        return _error(
            code="operation_failed",
            message="scene.write failed",
            data={"type": type(exc).__name__},
            started=started,
        )
