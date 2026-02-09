# -*- coding: utf-8 -*-
"""Info query implementation for retrieving Blender state and metadata."""
from __future__ import annotations

import base64
import logging
import tempfile
import os
import sys
from enum import Enum
from typing import Any

from ..response import (
    _ok, check_bpy_available, bpy_unavailable_error,
    invalid_params_error, operation_failed_error,
)

logger = logging.getLogger(__name__)


class InfoType(str, Enum):
    """Supported info query types."""
    REPORTS = "reports"
    LAST_OP = "last_op"
    UNDO_HISTORY = "undo_history"
    SCENE_STATS = "scene_stats"
    SELECTION = "selection"
    MODE = "mode"
    CHANGES = "changes"
    VIEWPORT_CAPTURE = "viewport_capture"
    VERSION = "version"
    MEMORY = "memory"


_last_op_info: dict[str, Any] = {}
_change_tracking: dict[str, set[str]] = {
    "modified_objects": set(),
    "added_objects": set(),
    "deleted_objects": set(),
}


def record_last_op(operator: str, success: bool, result: str, reports: list[dict[str, Any]], duration_ms: float, params: dict[str, Any]) -> None:
    """Record last operation info for later query."""
    global _last_op_info
    _last_op_info = {
        "operator": operator,
        "success": success,
        "result": result,
        "reports": reports,
        "duration_ms": duration_ms,
        "params": params,
    }


def info_query(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Execute an info.query operation.
    
    Args:
        payload: Query parameters:
            - type: Query type (reports, last_op, undo_history, etc.)
            - params: Type-specific parameters
        started: Start time for timing
        
    Returns:
        Response dict with query result
    """
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)
    
    query_type = payload.get("type")
    if not query_type:
        return invalid_params_error("'type' parameter is required", started)
    
    try:
        info_type = InfoType(query_type.lower())
    except ValueError:
        valid_types = [t.value for t in InfoType]
        return invalid_params_error(
            f"Invalid query type: {query_type}. Valid types: {valid_types}",
            started,
        )
    
    params = payload.get("params", {})
    
    try:
        if info_type == InfoType.REPORTS:
            result = _query_reports(bpy, params)
        elif info_type == InfoType.LAST_OP:
            result = _query_last_op(bpy, params)
        elif info_type == InfoType.UNDO_HISTORY:
            result = _query_undo_history(bpy, params)
        elif info_type == InfoType.SCENE_STATS:
            result = _query_scene_stats(bpy, params)
        elif info_type == InfoType.SELECTION:
            result = _query_selection(bpy, params)
        elif info_type == InfoType.MODE:
            result = _query_mode(bpy, params)
        elif info_type == InfoType.CHANGES:
            result = _query_changes(bpy, params)
        elif info_type == InfoType.VIEWPORT_CAPTURE:
            result = _query_viewport_capture(bpy, params)
        elif info_type == InfoType.VERSION:
            result = _query_version(bpy, params)
        elif info_type == InfoType.MEMORY:
            result = _query_memory(bpy, params)
        else:
            return invalid_params_error(f"Query type not implemented: {query_type}", started)
        
        return _ok(result=result, started=started)
    except Exception as exc:
        return operation_failed_error("info.query", exc, started)


def _query_reports(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query recent operation reports."""
    limit = params.get("limit", 50)
    
    reports = []
    try:
        wm = bpy.context.window_manager
        if hasattr(wm, "reports"):
            for report in list(wm.reports)[-limit:]:
                reports.append({
                    "type": report.type,
                    "message": report.message,
                })
    except Exception as exc:
        logger.debug("Failed to query reports: %s", exc)
    
    return {"reports": reports, "count": len(reports)}


def _query_last_op(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query last executed operation info."""
    if _last_op_info:
        return dict(_last_op_info)
    
    return {
        "operator": None,
        "success": None,
        "result": None,
        "reports": [],
        "duration_ms": None,
        "params": {},
    }


def _query_undo_history(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query undo history."""
    history = []
    current_step = 0
    
    try:
        wm = bpy.context.window_manager
        if hasattr(wm, "undo_stack"):
            for i, step in enumerate(wm.undo_stack):
                history.append({
                    "index": i,
                    "name": step.name if hasattr(step, "name") else f"Step {i}",
                })
                if hasattr(step, "is_current") and step.is_current:
                    current_step = i
    except Exception as exc:
        logger.debug("Failed to query undo history: %s", exc)
    
    return {
        "history": history,
        "current_step": current_step,
        "can_undo": len(history) > 0 and current_step > 0,
        "can_redo": len(history) > 0 and current_step < len(history) - 1,
    }


def _query_scene_stats(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query scene statistics."""
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    
    total_verts = 0
    total_edges = 0
    total_faces = 0
    mesh_objects = 0
    
    for obj in scene.objects:
        if obj.type == 'MESH':
            mesh_objects += 1
            try:
                obj_eval = obj.evaluated_get(depsgraph)
                mesh = obj_eval.to_mesh()
                if mesh:
                    total_verts += len(mesh.vertices)
                    total_edges += len(mesh.edges)
                    total_faces += len(mesh.polygons)
                    obj_eval.to_mesh_clear()
            except Exception as exc:
                logger.debug("Failed to evaluate mesh for '%s': %s", obj.name, exc)
    
    memory_stats = {}
    try:
        if hasattr(bpy.utils, "resource_path"):
            import resource
            mem_info = resource.getrusage(resource.RUSAGE_SELF)
            memory_stats["peak_mb"] = mem_info.ru_maxrss / 1024.0
    except Exception as exc:
        logger.debug("Failed to query memory stats: %s", exc)
    
    return {
        "scene_name": scene.name,
        "object_count": len(scene.objects),
        "mesh_objects": mesh_objects,
        "vertex_count": total_verts,
        "edge_count": total_edges,
        "face_count": total_faces,
        "render_engine": scene.render.engine,
        "frame_current": scene.frame_current,
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "memory": memory_stats,
    }


def _query_selection(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query current selection state."""
    ctx = bpy.context
    mode = ctx.mode
    
    try:
        active = ctx.active_object
        active_name = active.name if active else None
    except Exception:
        active_name = None
    
    try:
        selected = list(ctx.selected_objects)
        selected_names = [obj.name for obj in selected]
    except Exception:
        selected = []
        selected_names = []
    
    result = {
        "mode": mode,
        "active_object": active_name,
        "selected_objects": selected_names,
        "selected_count": len(selected),
    }
    
    if mode == "EDIT_MESH" and active_name:
        obj = ctx.active_object
        if obj.type == 'MESH':
            import bmesh
            bm = bmesh.from_edit_mesh(obj.data)
            result["edit_mesh"] = {
                "selected_verts": len([v for v in bm.verts if v.select]),
                "selected_edges": len([e for e in bm.edges if e.select]),
                "selected_faces": len([f for f in bm.faces if f.select]),
                "total_verts": len(bm.verts),
                "total_edges": len(bm.edges),
                "total_faces": len(bm.faces),
            }
    
    return result


def _query_mode(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query current editing mode."""
    ctx = bpy.context
    
    mode_string = ctx.mode
    mode_map = {
        "OBJECT": "Object Mode",
        "EDIT_MESH": "Edit Mode",
        "EDIT_CURVE": "Edit Mode (Curve)",
        "EDIT_SURFACE": "Edit Mode (Surface)",
        "EDIT_TEXT": "Edit Mode (Text)",
        "EDIT_ARMATURE": "Edit Mode (Armature)",
        "EDIT_METABALL": "Edit Mode (Metaball)",
        "EDIT_LATTICE": "Edit Mode (Lattice)",
        "POSE": "Pose Mode",
        "SCULPT": "Sculpt Mode",
        "PAINT_WEIGHT": "Weight Paint",
        "PAINT_VERTEX": "Vertex Paint",
        "PAINT_TEXTURE": "Texture Paint",
        "PARTICLE": "Particle Edit",
        "PAINT_GPENCIL": "Draw (Grease Pencil)",
        "EDIT_GPENCIL": "Edit (Grease Pencil)",
        "SCULPT_GPENCIL": "Sculpt (Grease Pencil)",
        "WEIGHT_GPENCIL": "Weight (Grease Pencil)",
    }
    
    active_tool = None
    try:
        if ctx.workspace and ctx.workspace.tools:
            for tool in ctx.workspace.tools:
                if tool.mode == mode_string:
                    active_tool = tool.idname
                    break
    except Exception:
        pass
    
    return {
        "mode": mode_string,
        "mode_string": mode_map.get(mode_string, mode_string),
        "active_object": ctx.active_object.name if ctx.active_object else None,
        "object_type": ctx.active_object.type if ctx.active_object else None,
        "tool": active_tool,
        "workspace": ctx.workspace.name if ctx.workspace else None,
    }


def _query_changes(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query changes since last query (basic implementation)."""
    global _change_tracking
    
    result = {
        "modified_objects": list(_change_tracking["modified_objects"]),
        "added_objects": list(_change_tracking["added_objects"]),
        "deleted_objects": list(_change_tracking["deleted_objects"]),
    }
    
    if params.get("clear", True):
        _change_tracking = {
            "modified_objects": set(),
            "added_objects": set(),
            "deleted_objects": set(),
        }
    
    return result


def _query_viewport_capture(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Capture viewport image."""
    output_format = params.get("format", "base64")
    resolution = params.get("resolution")
    shading = params.get("shading")
    
    screen = getattr(bpy.context, "screen", None)
    if screen is None:
        raise RuntimeError(
            "No screen context available. Viewport capture requires a GUI "
            "window and cannot run in headless or background mode."
        )
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        original_shading = space.shading.type
                        if shading:
                            space.shading.type = shading.upper()
                        
                        try:
                            override = {
                                "area": area,
                                "region": [r for r in area.regions if r.type == 'WINDOW'][0],
                            }
                            
                            if resolution:
                                with bpy.context.temp_override(**override):
                                    bpy.ops.render.opengl(write_still=True)
                                    bpy.data.images["Render Result"].save_render(tmp_path)
                            else:
                                with bpy.context.temp_override(**override):
                                    bpy.ops.screen.screenshot(filepath=tmp_path)
                        finally:
                            if shading:
                                space.shading.type = original_shading
                        
                        break
                break
        
        if output_format == "base64":
            with open(tmp_path, "rb") as f:
                data = f.read()
            
            import struct
            width, height = 0, 0
            if len(data) > 24:
                w, h = struct.unpack(">II", data[16:24])
                width, height = w, h
            
            return {
                "format": "base64",
                "data": base64.b64encode(data).decode("utf-8"),
                "width": width,
                "height": height,
                "mime_type": "image/png",
            }
        else:
            return {
                "format": "filepath",
                "filepath": tmp_path,
            }
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _query_version(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query Blender version information."""
    return {
        "blender_version": list(bpy.app.version),
        "blender_version_string": bpy.app.version_string,
        "api_version": list(bpy.app.version) if hasattr(bpy.app, "version") else None,
        "python_version": sys.version,
        "python_version_info": list(sys.version_info[:3]),
        "build_date": bpy.app.build_date.decode() if hasattr(bpy.app, "build_date") else None,
        "build_hash": bpy.app.build_hash.decode() if hasattr(bpy.app, "build_hash") else None,
    }


def _query_memory(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query memory usage."""
    result = {
        "total_mb": None,
        "used_mb": None,
        "peak_mb": None,
    }
    
    try:
        import psutil
        process = psutil.Process()
        mem_info = process.memory_info()
        result["used_mb"] = mem_info.rss / (1024 * 1024)
        result["peak_mb"] = mem_info.peak_wset / (1024 * 1024) if hasattr(mem_info, "peak_wset") else None
        
        vm = psutil.virtual_memory()
        result["total_mb"] = vm.total / (1024 * 1024)
    except ImportError:
        pass
    except Exception:
        pass
    
    categories = {}
    try:
        categories["meshes"] = sum(
            m.calc_loop_triangles_count() * 12 if hasattr(m, "calc_loop_triangles_count") else 0
            for m in bpy.data.meshes
        ) / (1024 * 1024)
        categories["images"] = sum(
            img.size[0] * img.size[1] * img.channels * (4 if img.is_float else 1)
            for img in bpy.data.images if img.size[0] > 0
        ) / (1024 * 1024)
    except Exception:
        pass
    
    result["categories"] = categories
    
    return result
