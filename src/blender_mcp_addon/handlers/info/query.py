# -*- coding: utf-8 -*-
"""Info query implementation for retrieving Blender state and metadata."""

from __future__ import annotations

import base64
import logging
import os
import sys
import tempfile
from enum import Enum
from typing import Any

from ..response import (
    _ok,
    bpy_unavailable_error,
    check_bpy_available,
    invalid_params_error,
    operation_failed_error,
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
    NODE_TYPES = "node_types"
    WORLD = "world"
    DEPSGRAPH = "depsgraph"
    BATCH = "batch"


_last_op_info: dict[str, Any] = {}
_change_tracking: dict[str, set[str]] = {
    "modified_objects": set(),
    "added_objects": set(),
    "deleted_objects": set(),
}

# Module-level constant for mode string mapping - avoids rebuilding dict every call
_MODE_MAP = {
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


def record_last_op(
    operator: str,
    success: bool,
    result: str,
    reports: list[dict[str, Any]],
    duration_ms: float,
    params: dict[str, Any],
) -> None:
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
        elif info_type == InfoType.NODE_TYPES:
            result = _query_node_types(bpy, params)
        elif info_type == InfoType.WORLD:
            result = _query_world(bpy, params)
        elif info_type == InfoType.DEPSGRAPH:
            result = _query_depsgraph(bpy, params)
        elif info_type == InfoType.BATCH:
            result = _query_batch(bpy, params)
        else:
            return invalid_params_error(f"Query type not implemented: {query_type}", started)

        return _ok(result=result, started=started)
    except (AttributeError, KeyError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("info.query", exc, started)


def _query_batch(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Batch query multiple info types in a single call."""
    types = params.get("types", [])
    results = {}
    for query_type in types:
        try:
            if query_type == "scene_stats":
                results["scene_stats"] = _query_scene_stats(bpy, {})
            elif query_type == "version":
                results["version"] = _query_version(bpy, {})
            elif query_type == "memory":
                results["memory"] = _query_memory(bpy, {})
            elif query_type == "world":
                results["world"] = _query_world(bpy, {})
            elif query_type == "depsgraph":
                results["depsgraph"] = _query_depsgraph(bpy, {})
        except (AttributeError, KeyError, TypeError, RuntimeError, ValueError) as exc:
            logger.debug("Batch query failed for %s: %s", query_type, exc)
            results[query_type] = {"error": str(exc)}
    return results


def _query_world(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query world/environment settings."""
    world = bpy.context.scene.world
    if world is None:
        return {"world": None, "color": [0.05, 0.05, 0.05]}

    result = {"name": world.name}

    if world.use_nodes and world.node_tree:
        result["use_nodes"] = True
        result["node_tree"] = world.node_tree.name
    else:
        result["use_nodes"] = False

    if hasattr(world, "color"):
        result["color"] = list(world.color)

    return result


def _query_depsgraph(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query depsgraph statistics."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    return {
        "updates": len(list(depsgraph.updates)),
        "view_layer": bpy.context.view_layer.name if bpy.context.view_layer else None,
    }


def _query_reports(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query recent operation reports."""
    limit = params.get("limit", 50)

    reports = []
    try:
        wm = bpy.context.window_manager
        if hasattr(wm, "reports"):
            for report in list(wm.reports)[-limit:]:
                reports.append(
                    {
                        "type": report.type,
                        "message": report.message,
                    }
                )
    except (AttributeError, KeyError, RuntimeError) as exc:
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
                history.append(
                    {
                        "index": i,
                        "name": step.name if hasattr(step, "name") else f"Step {i}",
                    }
                )
                if hasattr(step, "is_current") and step.is_current:
                    current_step = i
    except (AttributeError, RuntimeError) as exc:
        logger.debug("Failed to query undo history: %s", exc)

    return {
        "history": history,
        "current_step": current_step,
        "can_undo": len(history) > 0 and current_step > 0,
        "can_redo": len(history) > 0 and current_step < len(history) - 1,
    }


def _query_scene_stats(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query scene statistics.

    Args:
        bpy: Blender Python API module
        params: Query parameters:
            - use_evaluated: bool (default: False)
              If True, evaluates mesh modifiers and returns accurate vertex/edge/face counts.
              WARNING: This is extremely expensive for complex scenes - calls to_mesh() for every MESH object.
              If False (default), uses original mesh data without evaluating modifiers (much faster).

    Returns:
        Dict with scene statistics including object counts, vertex/edge/face counts, render settings.
    """
    use_evaluated = params.get("use_evaluated", False)
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get() if use_evaluated else None

    total_verts = 0
    total_edges = 0
    total_faces = 0
    mesh_objects = 0

    for obj in scene.objects:
        if obj.type == "MESH":
            mesh_objects += 1
            if use_evaluated and depsgraph:
                obj_eval = obj.evaluated_get(depsgraph)
                try:
                    mesh = obj_eval.to_mesh()
                    if mesh:
                        total_verts += len(mesh.vertices)
                        total_edges += len(mesh.edges)
                        total_faces += len(mesh.polygons)
                except (AttributeError, RuntimeError, ValueError) as exc:
                    logger.debug("Failed to evaluate mesh for '%s': %s", obj.name, exc)
                finally:
                    obj_eval.to_mesh_clear()
            else:
                if obj.data is not None:
                    mesh = obj.data
                    total_verts += len(mesh.vertices)
                    total_edges += len(mesh.edges)
                    total_faces += len(mesh.polygons)

    memory_stats = {}
    try:
        if hasattr(bpy.utils, "resource_path"):
            import resource

            mem_info = resource.getrusage(resource.RUSAGE_SELF)
            memory_stats["peak_mb"] = mem_info.ru_maxrss / 1024.0
    except (ImportError, AttributeError, OSError) as exc:
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
    try:
        mode = bpy.context.mode
    except (AttributeError, RuntimeError):
        mode = "OBJECT"

    try:
        active = bpy.context.view_layer.objects.active
        active_name = active.name if active else None
    except (AttributeError, RuntimeError):
        active_name = None

    selected_names = []
    try:
        for obj in bpy.context.view_layer.objects:
            try:
                if obj.select_get():
                    selected_names.append(obj.name)
            except (AttributeError, RuntimeError):
                pass
    except (AttributeError, RuntimeError):
        pass

    result = {
        "mode": mode,
        "active_object": active_name,
        "selected_objects": selected_names,
        "selected_count": len(selected_names),
    }

    if mode == "EDIT_MESH" and active_name:
        try:
            obj = bpy.context.view_layer.objects.active
            if obj is not None and obj.type == "MESH" and obj.data is not None:
                import bmesh

                bm = bmesh.from_edit_mesh(obj.data)
                sel_verts = sum(1 for v in bm.verts if v.select)
                sel_edges = sum(1 for e in bm.edges if e.select)
                sel_faces = sum(1 for f in bm.faces if f.select)
                result["edit_mesh"] = {
                    "selected_verts": sel_verts,
                    "selected_edges": sel_edges,
                    "selected_faces": sel_faces,
                    "total_verts": len(bm.verts),
                    "total_edges": len(bm.edges),
                    "total_faces": len(bm.faces),
                }
        except (AttributeError, RuntimeError, ImportError) as exc:
            logger.debug("Failed to query edit mesh selection: %s", exc)

    # Query Node Editor selection state
    node_editor = _query_node_editor_selection(bpy)
    if node_editor is not None:
        result["node_editor"] = node_editor

    return result


def _query_node_editor_selection(bpy: Any) -> dict[str, Any] | None:
    """Query node editor selection state if a node editor is active."""
    try:
        screen = bpy.context.screen
        if screen is None:
            return None

        for area in screen.areas:
            if area.type == "NODE_EDITOR":
                for space in area.spaces:
                    if space.type == "NODE_EDITOR" and space.node_tree:
                        tree = space.node_tree
                        selected_nodes = []
                        active_node_info = None

                        # Detect if we're inside a node group (nested editing)
                        # space.path contains the hierarchy of node trees being edited
                        parent_context = None
                        current_tree_name = tree.name
                        current_tree = tree

                        if hasattr(space, "path") and len(space.path) > 1:
                            # We're inside a nested node group
                            path_entries = []
                            for i, path_item in enumerate(space.path):
                                node_name = None
                                if hasattr(path_item, "node") and path_item.node:
                                    node_name = path_item.node.name
                                path_entries.append({
                                    "tree_name": path_item.node_tree.name if path_item.node_tree else None,
                                    "node_name": node_name,
                                })
                            parent_context = path_entries
                            # The current tree being edited is the last item in path
                            if space.path[-1].node_tree:
                                current_tree = space.path[-1].node_tree
                                current_tree_name = current_tree.name

                        # Use current_tree (which may be a nested group) instead of tree
                        for node in current_tree.nodes:
                            try:
                                if node.select:
                                    node_info = _read_selected_node_detail(node)
                                    selected_nodes.append(node_info)
                            except (AttributeError, RuntimeError):
                                pass

                        try:
                            active_node = current_tree.nodes.active
                            if active_node:
                                active_node_info = _read_selected_node_detail(active_node)
                        except (AttributeError, RuntimeError):
                            pass

                        tree_type_map = {
                            "ShaderNodeTree": "SHADER",
                            "CompositorNodeTree": "COMPOSITOR",
                            "GeometryNodeTree": "GEOMETRY",
                        }

                        result = {
                            "tree_type": tree_type_map.get(current_tree.bl_idname, current_tree.bl_idname),
                            "tree_name": current_tree_name,
                            "selected_nodes": selected_nodes,
                            "selected_count": len(selected_nodes),
                            "active_node": active_node_info,
                        }

                        if parent_context:
                            result["nested_path"] = parent_context

                        return result
    except (AttributeError, RuntimeError) as exc:
        logger.debug("Failed to query node editor selection: %s", exc)

    return None


def _read_selected_node_detail(node: Any) -> dict[str, Any]:
    """Read detailed info for a selected node including inputs/outputs."""
    node_info: dict[str, Any] = {
        "name": node.name,
        "type": node.bl_idname,
        "label": node.label or node.name,
        "location": [node.location.x, node.location.y],
    }

    if node.type == "GROUP" and hasattr(node, "node_tree") and node.node_tree:
        node_info["is_group"] = True
        node_info["group_tree_name"] = node.node_tree.name

    # Read inputs with values
    inputs = []
    for inp in node.inputs:
        inp_data: dict[str, Any] = {"name": inp.name, "type": inp.type}
        if hasattr(inp, "default_value"):
            try:
                val = inp.default_value
                if hasattr(val, "__len__") and not isinstance(val, str):
                    inp_data["value"] = list(val)
                else:
                    inp_data["value"] = val
            except (AttributeError, ValueError):
                inp_data["value"] = "<unreadable>"
        inp_data["is_linked"] = inp.is_linked
        if inp.is_linked:
            try:
                link = inp.links[0]
                inp_data["linked_from"] = {
                    "node": link.from_node.name,
                    "socket": link.from_socket.name,
                }
            except (AttributeError, IndexError):
                pass
        inputs.append(inp_data)
    node_info["inputs"] = inputs

    # Read outputs
    outputs = []
    for out in node.outputs:
        out_data: dict[str, Any] = {"name": out.name, "type": out.type, "is_linked": out.is_linked}
        if out.is_linked:
            try:
                out_data["links"] = [
                    {"node": link.to_node.name, "socket": link.to_socket.name}
                    for link in out.links
                ]
            except (AttributeError, IndexError):
                pass
        outputs.append(out_data)
    node_info["outputs"] = outputs

    return node_info


def _query_mode(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query current editing mode."""
    ctx = bpy.context

    mode_string = ctx.mode

    active_tool = None
    try:
        if ctx.workspace and ctx.workspace.tools:
            for tool in ctx.workspace.tools:
                if tool.mode == mode_string:
                    active_tool = tool.idname
                    break
    except (AttributeError, RuntimeError):
        pass

    return {
        "mode": mode_string,
        "mode_string": _MODE_MAP.get(mode_string, mode_string),
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
    """Capture viewport image with optional thumbnail compression."""
    image_format = params.get("format", "JPEG")
    output_format = params.get("output", "base64")
    resolution = params.get("resolution")
    shading = params.get("shading")
    thumbnail = params.get("thumbnail", True)
    max_size = params.get("max_size", 320)

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
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        original_shading = space.shading.type
                        if shading:
                            space.shading.type = shading.upper()

                        try:
                            override = {
                                "area": area,
                                "region": [r for r in area.regions if r.type == "WINDOW"][0],
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

        if output_format == "filepath":
            return {
                "format": "filepath",
                "filepath": tmp_path,
            }

        image_data, width, height, mime_type = _encode_image(
            bpy,
            tmp_path,
            thumbnail=thumbnail,
            max_size=max_size,
            image_format=image_format,
        )
        return {
            "format": "base64",
            "data": image_data,
            "width": width,
            "height": height,
            "mime_type": mime_type,
        }
    except (AttributeError, RuntimeError, OSError, IndexError):
        raise
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _encode_image(
    bpy: Any,
    filepath: str,
    *,
    thumbnail: bool = True,
    max_size: int = 320,
    image_format: str = "JPEG",
) -> tuple[str, int, int, str]:
    """Load image from *filepath*, optionally resize, return (base64, w, h, mime)."""
    with open(filepath, "rb") as f:
        raw_data = f.read()

    import struct

    width, height = 0, 0
    if len(raw_data) > 24:
        width, height = struct.unpack(">II", raw_data[16:24])

    if not thumbnail or width == 0 or height == 0:
        return base64.b64encode(raw_data).decode("utf-8"), width, height, "image/png"

    if image_format.upper() == "PNG":
        return base64.b64encode(raw_data).decode("utf-8"), width, height, "image/png"

    if width <= max_size and height <= max_size:
        return base64.b64encode(raw_data).decode("utf-8"), width, height, "image/png"

    img = bpy.data.images.load(filepath, check_existing=False)
    original_quality = None
    try:
        scale = max_size / max(width, height)
        new_w = max(1, int(width * scale))
        new_h = max(1, int(height * scale))
        img.scale(new_w, new_h)

        thumb_path = filepath + "_thumb.jpg"
        img.filepath_raw = thumb_path
        img.file_format = "JPEG"
        # Save original quality and restore after
        original_quality = bpy.context.scene.render.image_settings.quality
        bpy.context.scene.render.image_settings.quality = 50
        img.save()

        with open(thumb_path, "rb") as f:
            thumb_data = f.read()
        if os.path.exists(thumb_path):
            os.remove(thumb_path)

        return (
            base64.b64encode(thumb_data).decode("utf-8"),
            new_w,
            new_h,
            "image/jpeg",
        )
    finally:
        # Restore original quality setting
        if original_quality is not None:
            bpy.context.scene.render.image_settings.quality = original_quality
        bpy.data.images.remove(img)


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
    except (AttributeError, OSError, RuntimeError):
        pass

    categories = {}
    try:
        categories["meshes"] = sum(
            m.calc_loop_triangles_count() * 12 if hasattr(m, "calc_loop_triangles_count") else 0
            for m in bpy.data.meshes
        ) / (1024 * 1024)
        categories["images"] = sum(
            img.size[0] * img.size[1] * img.channels * (4 if img.is_float else 1)
            for img in bpy.data.images
            if img.size[0] > 0
        ) / (1024 * 1024)
    except (AttributeError, TypeError, ZeroDivisionError):
        pass

    result["categories"] = categories

    return result


def _query_node_types(bpy: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Query available node types — dynamically discovered from bpy.types."""
    from ..nodes.editor import _discover_node_types

    filter_prefix = params.get("prefix", "")
    types = _discover_node_types()
    if filter_prefix:
        prefix = filter_prefix.lower()
        types = [t for t in types if t["bl_idname"].lower().startswith(prefix) or t["name"].lower().startswith(prefix)]
    return {
        "count": len(types),
        "types": types,
    }
