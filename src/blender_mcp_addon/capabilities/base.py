# -*- coding: utf-8 -*-
"""Base capability dispatcher and helpers.

Routes internal capabilities (data.*, operator.execute, info.query,
script.execute) and new blender.* capabilities from the 26-tool architecture.
"""
from __future__ import annotations

import time
from typing import Any

from ..handlers.data.dispatcher import (
    data_create,
    data_delete,
    data_link,
    data_list,
    data_read,
    data_write,
)
from ..handlers.info import info_query
from ..handlers.operator import operator_execute
from ..handlers.response import _error, _ok
from ..handlers.script import script_execute

from ..handlers import data as _data_handlers  # noqa: F401 - Import to register handlers


def _dispatch_new_capability(capability: str, payload: dict[str, Any], started: float) -> dict[str, Any]:
    """Dispatch new blender.* capabilities.
    
    Maps the 26 new tool internal capabilities to handler calls.
    Many new tools reuse existing handlers with parameter transformations.
    New handlers that require bpy are imported lazily.
    """
    # ---------------------------------------------------------------
    # Perception Layer — map to existing handlers where possible
    # ---------------------------------------------------------------
    if capability == "blender.get_objects":
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
        return data_list({"type": "object", "filter": filter_dict}, started=started)

    if capability == "blender.get_object_data":
        read_params = {}
        if "include" in payload:
            read_params["include"] = payload["include"]
        return data_read({"type": "object", "name": payload.get("name", ""), "params": read_params}, started=started)

    if capability == "blender.get_node_tree":
        from ..handlers.nodes.reader import node_tree_read
        return node_tree_read(payload, started=started)

    if capability == "blender.get_animation_data":
        from ..handlers.animation.reader import animation_read
        return animation_read(payload, started=started)

    if capability == "blender.get_materials":
        return data_list({"type": "material", **payload}, started=started)

    if capability == "blender.get_scene":
        include = payload.get("include", ["stats", "render", "timeline"])
        result: dict[str, Any] = {}
        # stats, render, timeline all come from scene_stats query
        if any(s in include for s in ("stats", "render", "timeline")):
            stats_resp = info_query({"type": "scene_stats"}, started=started)
            if stats_resp.get("ok"):
                stats = stats_resp.get("result", {})
                if "stats" in include:
                    result["stats"] = {
                        "scene_name": stats.get("scene_name"),
                        "object_count": stats.get("object_count"),
                        "mesh_objects": stats.get("mesh_objects"),
                        "vertex_count": stats.get("vertex_count"),
                        "edge_count": stats.get("edge_count"),
                        "face_count": stats.get("face_count"),
                    }
                if "render" in include:
                    result["render"] = {
                        "engine": stats.get("render_engine"),
                        "resolution": stats.get("resolution"),
                    }
                if "timeline" in include:
                    result["timeline"] = {
                        "frame_current": stats.get("frame_current"),
                        "frame_start": stats.get("frame_start"),
                        "frame_end": stats.get("frame_end"),
                    }
        if "version" in include:
            ver_resp = info_query({"type": "version"}, started=started)
            if ver_resp.get("ok"):
                result["version"] = ver_resp.get("result", {})
        if "memory" in include:
            mem_resp = info_query({"type": "memory"}, started=started)
            if mem_resp.get("ok"):
                result["memory"] = mem_resp.get("result", {})
        if "world" in include:
            try:
                import bpy  # type: ignore
                world = bpy.context.scene.world
                if world:
                    world_info: dict[str, Any] = {"name": world.name, "use_nodes": world.use_nodes}
                    if world.use_nodes and world.node_tree:
                        bg = world.node_tree.nodes.get("Background")
                        if bg:
                            world_info["background_color"] = list(bg.inputs["Color"].default_value)
                            world_info["background_strength"] = bg.inputs["Strength"].default_value
                    result["world"] = world_info
            except Exception:
                pass
        return _ok(result=result, started=started)

    if capability == "blender.get_collections":
        read_params = {}
        if "depth" in payload:
            read_params["max_depth"] = payload["depth"]
        return data_read({"type": "collection", "name": payload.get("root", "Scene Collection"), "params": read_params}, started=started)

    if capability == "blender.get_armature_data":
        read_params = {}
        if "include" in payload:
            read_params["include"] = payload["include"]
        if "bone_filter" in payload:
            read_params["bone_filter"] = payload["bone_filter"]
        return data_read({"type": "armature", "name": payload.get("armature_name", ""), "params": read_params}, started=started)

    if capability == "blender.get_images":
        from ..handlers.data.image_handler import image_list
        return image_list(payload, started=started)

    if capability == "blender.capture_viewport":
        capture_params = {}
        if "shading" in payload:
            capture_params["shading"] = payload["shading"]
        if "camera_view" in payload:
            capture_params["camera_view"] = payload["camera_view"]
        if "format" in payload:
            capture_params["format"] = payload["format"]
        return info_query({"type": "viewport_capture", "params": capture_params}, started=started)

    if capability == "blender.get_selection":
        return info_query({"type": "selection"}, started=started)

    # ---------------------------------------------------------------
    # Declarative Write Layer
    # ---------------------------------------------------------------
    if capability == "blender.edit_nodes":
        from ..handlers.nodes.editor import node_tree_edit
        return node_tree_edit(payload, started=started)

    if capability == "blender.edit_animation":
        from ..handlers.animation.editor import animation_edit
        return animation_edit(payload, started=started)

    if capability == "blender.edit_sequencer":
        from ..handlers.sequencer.editor import sequencer_edit
        return sequencer_edit(payload, started=started)

    # ---------------------------------------------------------------
    # Imperative Write Layer
    # ---------------------------------------------------------------
    if capability == "blender.create_object":
        return data_create({"type": "object", **payload}, started=started)

    if capability == "blender.modify_object":
        obj_name = payload.get("name", "")
        if payload.get("delete"):
            return data_delete({"type": "object", "name": obj_name, "params": {"delete_data": payload.get("delete_data", True)}}, started=started)
        # Handle set_origin via operator
        if "origin" in payload:
            origin_map = {"GEOMETRY": "ORIGIN_GEOMETRY", "CURSOR": "ORIGIN_CURSOR", "MEDIAN": "ORIGIN_CENTER_OF_MASS"}
            origin_type = origin_map.get(payload["origin"], payload["origin"])
            operator_execute({"operator": "object.origin_set", "params": {"type": origin_type}, "context": {"active_object": obj_name}}, started=started)
        # Build properties dict from flat schema params
        props: dict[str, Any] = {}
        if "location" in payload:
            props["location"] = payload["location"]
        if "rotation" in payload:
            props["rotation_euler"] = payload["rotation"]
        if "scale" in payload:
            props["scale"] = payload["scale"]
        if "parent" in payload:
            props["parent"] = payload["parent"] if payload["parent"] else None
        if "visible" in payload:
            props["visible"] = payload["visible"]
        if "hide_render" in payload:
            props["hide_render"] = payload["hide_render"]
        if "active" in payload:
            props["active"] = payload["active"]
        if "selected" in payload:
            props["selected"] = payload["selected"]
        if "new_name" in payload:
            props["name"] = payload["new_name"]
        if not props:
            return _ok(result={"name": obj_name, "modified": []}, started=started)
        return data_write({"type": "object", "name": obj_name, "properties": props}, started=started)

    if capability == "blender.manage_material":
        action = payload.get("action", "")
        name = payload.get("name", "")
        if action == "create":
            mat_params: dict[str, Any] = {}
            for k in ("base_color", "metallic", "roughness", "specular", "alpha",
                       "emission_color", "emission_strength", "use_fake_user"):
                if k in payload:
                    mat_params[k] = payload[k]
            return data_create({"type": "material", "name": name, "params": mat_params}, started=started)
        elif action == "delete":
            return data_delete({"type": "material", "name": name}, started=started)
        elif action in ("assign", "unassign"):
            return data_link({
                "source": {"type": "material", "name": name},
                "target": {"type": "object", "name": payload.get("object_name", "")},
                "unlink": action == "unassign",
                "params": {"slot": payload.get("slot")},
            }, started=started)
        else:
            # edit action — build properties dict from PBR params
            mat_props: dict[str, Any] = {}
            for k in ("base_color", "metallic", "roughness", "specular", "alpha",
                       "emission_color", "emission_strength", "use_fake_user"):
                if k in payload:
                    mat_props[k] = payload[k]
            return data_write({"type": "material", "name": name, "properties": mat_props}, started=started)

    if capability == "blender.manage_modifier":
        action = payload.get("action", "")
        obj = payload.get("object_name", "")
        mod_name = payload.get("modifier_name", "")
        if action == "add":
            return data_create({
                "type": "modifier", "name": mod_name,
                "object": obj, "modifier_type": payload.get("modifier_type", ""),
                **payload.get("settings", {}),
            }, started=started)
        elif action == "remove":
            return data_delete({"type": "modifier", "name": mod_name, "object": obj}, started=started)
        elif action == "configure":
            return data_write({"type": "modifier", "name": mod_name, "object": obj, **payload.get("settings", {})}, started=started)
        elif action in ("apply", "move_up", "move_down"):
            op_map = {"apply": "object.modifier_apply", "move_up": "object.modifier_move_up", "move_down": "object.modifier_move_down"}
            return operator_execute({"operator": op_map[action], "params": {"modifier": mod_name}, "context": {"active_object": obj}}, started=started)
        return _error(code="invalid_params", message=f"Unknown modifier action: {action}", started=started)

    if capability == "blender.manage_collection":
        action = payload.get("action", "")
        col_name = payload.get("collection_name", "")
        if action == "create":
            return data_create({"type": "collection", "name": col_name, "parent": payload.get("parent"), "color_tag": payload.get("color_tag")}, started=started)
        elif action == "delete":
            return data_delete({"type": "collection", "name": col_name}, started=started)
        elif action in ("link_object", "unlink_object"):
            return data_link({
                "type": "object", "name": payload.get("object_name", ""),
                "target": col_name,
                "action": "link" if action == "link_object" else "unlink",
            }, started=started)
        elif action == "set_visibility":
            return data_write({"type": "collection", "name": col_name,
                             "hide_viewport": payload.get("hide_viewport"),
                             "hide_render": payload.get("hide_render")}, started=started)
        elif action == "set_parent":
            return data_link({"type": "collection", "name": col_name, "target": payload.get("parent", ""), "action": "link"}, started=started)
        return _error(code="invalid_params", message=f"Unknown collection action: {action}", started=started)

    if capability == "blender.manage_uv":
        from ..handlers.uv.handler import uv_manage
        return uv_manage(payload, started=started)

    if capability == "blender.manage_constraints":
        from ..handlers.constraints.handler import constraints_manage
        return constraints_manage(payload, started=started)

    if capability == "blender.manage_physics":
        from ..handlers.physics.handler import physics_manage
        return physics_manage(payload, started=started)

    if capability == "blender.setup_scene":
        from ..handlers.scene.config import scene_setup
        return scene_setup(payload, started=started)

    # ---------------------------------------------------------------
    # Fallback Layer
    # ---------------------------------------------------------------
    if capability == "blender.execute_operator":
        return operator_execute({
            "operator": payload.get("operator", ""),
            "params": payload.get("params", {}),
            "context": payload.get("context"),
        }, started=started)

    if capability == "blender.execute_script":
        return script_execute(payload, started=started)

    if capability == "blender.import_export":
        from ..handlers.importexport.handler import import_export
        return import_export(payload, started=started)

    return _error(
        code="unsupported_capability",
        message=f"new capability '{capability}' not yet implemented",
        data={"capability": capability},
        started=started,
    )


def execute_capability(request: dict[str, Any]) -> dict[str, Any]:
    """Execute a capability request and return the result.
    
    Supports internal capabilities (data.*, operator.execute, info.query,
    script.execute) and new blender.* capabilities from the 26-tool architecture.
    """
    started = time.perf_counter()
    try:
        if not isinstance(request, dict):
            return _error(
                code="invalid_request",
                message="request must be a dict",
                data={"type": type(request).__name__},
                started=started,
            )

        capability = request.get("capability")
        if not isinstance(capability, str) or not capability.strip():
            return _error(
                code="invalid_request",
                message="missing or invalid 'capability'",
                data={"capability": capability},
                started=started,
            )

        payload = request.get("payload", {})
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            return _error(
                code="invalid_request",
                message="'payload' must be a dict",
                data={"type": type(payload).__name__},
                started=started,
            )

        # New blender.* capabilities (26-tool architecture)
        if capability.startswith("blender."):
            return _dispatch_new_capability(capability, payload, started)

        # Legacy unified tools
        if capability == "data.create":
            return data_create(payload, started=started)
        if capability == "data.read":
            return data_read(payload, started=started)
        if capability == "data.write":
            return data_write(payload, started=started)
        if capability == "data.delete":
            return data_delete(payload, started=started)
        if capability == "data.list":
            return data_list(payload, started=started)
        if capability == "data.link":
            return data_link(payload, started=started)
        if capability == "operator.execute":
            return operator_execute(payload, started=started)
        if capability == "info.query":
            return info_query(payload, started=started)
        if capability == "script.execute":
            return script_execute(payload, started=started)

        return _error(
            code="unsupported_capability",
            message="capability is not supported by this addon",
            data={"capability": capability},
            started=started,
        )
    except Exception as exc:
        return _error(
            code="addon_exception",
            message="unhandled addon exception",
            data={"type": type(exc).__name__, "message": str(exc)},
            started=started,
        )
