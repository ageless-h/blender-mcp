# -*- coding: utf-8 -*-
"""Perception layer handlers — 11 read-only tools."""

from __future__ import annotations

from typing import Any

from ..handlers.error_codes import ErrorCode
from ..handlers.info import info_query
from ..handlers.registry import HandlerRegistry
from ..handlers.response import _error, _ok, not_found_error, operation_failed_error
from ..handlers.types import DataType


def _handle_get_objects(payload: dict[str, Any], started: float) -> dict[str, Any]:
    filter_dict = {}
    if "type_filter" in payload:
        filter_dict["object_type"] = payload["type_filter"]
    if "selected_only" in payload:
        filter_dict["selected"] = payload["selected_only"]
    if "visible_only" in payload:
        filter_dict["visible"] = payload["visible_only"]
    if "name_pattern" in payload:
        filter_dict["name_pattern"] = payload["name_pattern"]
    if "collection" in payload:
        filter_dict["collection"] = payload["collection"]
    handler = HandlerRegistry.get(DataType.OBJECT)
    if handler is None:
        return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="object handler not available", started=started)
    try:
        return _ok(result=handler.list_items(filter_dict), started=started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("get_objects", exc, started)


def _handle_get_object_data(payload: dict[str, Any], started: float) -> dict[str, Any]:
    name = payload.get("name", "")
    read_params: dict[str, Any] = {}
    if "include" in payload:
        read_params["include"] = payload["include"]
    handler = HandlerRegistry.get(DataType.OBJECT)
    if handler is None:
        return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="object handler not available", started=started)
    try:
        return _ok(result=handler.read(name, None, read_params), started=started)
    except KeyError:
        return not_found_error("object", name, started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("get_object_data", exc, started)


def _handle_get_node_tree(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.nodes.reader import node_tree_read

    return node_tree_read(payload, started=started)


def _handle_get_animation_data(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.animation.reader import animation_read

    return animation_read(payload, started=started)


def _handle_get_materials(payload: dict[str, Any], started: float) -> dict[str, Any]:
    handler = HandlerRegistry.get(DataType.MATERIAL)
    if handler is None:
        return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="material handler not available", started=started)
    try:
        return _ok(result=handler.list_items(payload), started=started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("get_materials", exc, started)


def _handle_get_scene(payload: dict[str, Any], started: float) -> dict[str, Any]:
    include = payload.get("include", ["stats", "render", "timeline"])
    include_set = set(include) if not isinstance(include, set) else include
    result: dict[str, Any] = {}

    batch_types = []
    if include_set & {"stats", "render", "timeline"}:
        batch_types.append("scene_stats")
    if "world" in include_set:
        batch_types.append("world")
    if "version" in include_set:
        batch_types.append("version")
    if "memory" in include_set:
        batch_types.append("memory")
    if "depsgraph" in include_set:
        batch_types.append("depsgraph")

    if batch_types:
        batch_resp = info_query({"type": "batch", "params": {"types": batch_types}}, started=started)
        if batch_resp.get("ok"):
            batch_result = batch_resp.get("result", {})

            if "scene_stats" in batch_result:
                stats = batch_result["scene_stats"]
                if isinstance(stats, dict) and "error" not in stats:
                    if "stats" in include_set:
                        result["stats"] = {
                            "scene_name": stats.get("scene_name"),
                            "object_count": stats.get("object_count"),
                            "mesh_objects": stats.get("mesh_objects"),
                            "vertex_count": stats.get("vertex_count"),
                            "edge_count": stats.get("edge_count"),
                            "face_count": stats.get("face_count"),
                        }
                    if "render" in include_set:
                        result["render"] = {
                            "engine": stats.get("render_engine"),
                            "fps": stats.get("fps"),
                            "fps_base": stats.get("fps_base"),
                            "resolution_x": stats.get("resolution_x"),
                            "resolution_y": stats.get("resolution_y"),
                            "resolution_percentage": stats.get("resolution_percentage"),
                        }
                    if "timeline" in include_set:
                        result["timeline"] = {
                            "frame_start": stats.get("frame_start"),
                            "frame_end": stats.get("frame_end"),
                            "frame_current": stats.get("frame_current"),
                        }

            if "world" in include_set and "world" in batch_result:
                world_data = batch_result["world"]
                if isinstance(world_data, dict) and "error" not in world_data:
                    result["world"] = world_data

            if "version" in include_set and "version" in batch_result:
                version_data = batch_result["version"]
                if isinstance(version_data, dict) and "error" not in version_data:
                    result["version"] = version_data

            if "memory" in include_set and "memory" in batch_result:
                memory_data = batch_result["memory"]
                if isinstance(memory_data, dict) and "error" not in memory_data:
                    result["memory"] = memory_data

            if "depsgraph" in include_set and "depsgraph" in batch_result:
                depsgraph_data = batch_result["depsgraph"]
                if isinstance(depsgraph_data, dict) and "error" not in depsgraph_data:
                    result["depsgraph"] = depsgraph_data

    return _ok(result=result, started=started)


def _handle_get_collections(payload: dict[str, Any], started: float) -> dict[str, Any]:
    handler = HandlerRegistry.get(DataType.COLLECTION)
    if handler is None:
        return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="collection handler not available", started=started)
    read_params = {}
    if "depth" in payload:
        read_params["depth"] = payload["depth"]
    try:
        return _ok(result=handler.read("", None, read_params), started=started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("get_collections", exc, started)


def _handle_get_armature_data(payload: dict[str, Any], started: float) -> dict[str, Any]:
    handler = HandlerRegistry.get(DataType.ARMATURE)
    if handler is None:
        return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="armature handler not available", started=started)
    armature_name = payload.get("armature_name", "")
    if not armature_name:
        return _error(code=ErrorCode.INVALID_PARAMS, message="armature_name is required", started=started)
    read_params: dict[str, Any] = {}
    if "include" in payload:
        read_params["include"] = payload["include"]
    if "bone_filter" in payload:
        read_params["bone_filter"] = payload["bone_filter"]
    try:
        return _ok(result=handler.read(armature_name, None, read_params), started=started)
    except (KeyError, AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("get_armature_data", exc, started)


def _handle_get_images(payload: dict[str, Any], started: float) -> dict[str, Any]:
    handler = HandlerRegistry.get(DataType.IMAGE)
    if handler is None:
        return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="image handler not available", started=started)
    try:
        return _ok(result=handler.list_items(payload), started=started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("get_images", exc, started)


def _handle_capture_viewport(payload: dict[str, Any], started: float) -> dict[str, Any]:
    return info_query({"type": "viewport_capture", "params": payload}, started=started)


def _handle_get_selection(payload: dict[str, Any], started: float) -> dict[str, Any]:
    return info_query({"type": "selection", "params": payload}, started=started)


PERCEPTION_HANDLERS = {
    "blender.get_objects": _handle_get_objects,
    "blender.get_object_data": _handle_get_object_data,
    "blender.get_node_tree": _handle_get_node_tree,
    "blender.get_animation_data": _handle_get_animation_data,
    "blender.get_materials": _handle_get_materials,
    "blender.get_scene": _handle_get_scene,
    "blender.get_collections": _handle_get_collections,
    "blender.get_armature_data": _handle_get_armature_data,
    "blender.get_images": _handle_get_images,
    "blender.capture_viewport": _handle_capture_viewport,
    "blender.get_selection": _handle_get_selection,
}
