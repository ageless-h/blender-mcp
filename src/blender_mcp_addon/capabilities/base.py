# -*- coding: utf-8 -*-
"""Base capability dispatcher and helpers.

Routes internal capabilities (data.*, operator.execute, info.query,
script.execute) and new blender.* capabilities from the 26-tool architecture.
"""

from __future__ import annotations

import time
from typing import Any, Callable

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


# ---------------------------------------------------------------
# Individual capability handlers
# ---------------------------------------------------------------


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
    return data_list({"type": "object", "filter": filter_dict}, started=started)


def _handle_get_object_data(payload: dict[str, Any], started: float) -> dict[str, Any]:
    read_params = {}
    if "include" in payload:
        read_params["include"] = payload["include"]
    return data_read(
        {"type": "object", "name": payload.get("name", ""), "params": read_params},
        started=started,
    )


def _handle_get_node_tree(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.nodes.reader import node_tree_read

    return node_tree_read(payload, started=started)


def _handle_get_animation_data(
    payload: dict[str, Any], started: float
) -> dict[str, Any]:
    from ..handlers.animation.reader import animation_read

    return animation_read(payload, started=started)


def _handle_get_materials(payload: dict[str, Any], started: float) -> dict[str, Any]:
    return data_list({"type": "material", **payload}, started=started)


def _handle_get_scene(payload: dict[str, Any], started: float) -> dict[str, Any]:
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
                world_info: dict[str, Any] = {
                    "name": world.name,
                    "use_nodes": world.use_nodes,
                }
                if world.use_nodes and world.node_tree:
                    bg = world.node_tree.nodes.get("Background")
                    if bg:
                        world_info["background_color"] = list(
                            bg.inputs["Color"].default_value
                        )
                        world_info["background_strength"] = bg.inputs[
                            "Strength"
                        ].default_value
                result["world"] = world_info
        except Exception:
            pass
    return _ok(result=result, started=started)


def _handle_get_collections(payload: dict[str, Any], started: float) -> dict[str, Any]:
    read_params = {}
    if "depth" in payload:
        read_params["max_depth"] = payload["depth"]
    return data_read(
        {"type": "collection", "name": payload.get("root", ""), "params": read_params},
        started=started,
    )


def _handle_get_armature_data(
    payload: dict[str, Any], started: float
) -> dict[str, Any]:
    read_params = {}
    if "include" in payload:
        read_params["include"] = payload["include"]
    if "bone_filter" in payload:
        read_params["bone_filter"] = payload["bone_filter"]
    return data_read(
        {
            "type": "armature",
            "name": payload.get("armature_name", ""),
            "params": read_params,
        },
        started=started,
    )


def _handle_get_images(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.data.image_handler import image_list

    return image_list(payload, started=started)


def _handle_capture_viewport(payload: dict[str, Any], started: float) -> dict[str, Any]:
    capture_params = {}
    if "shading" in payload:
        capture_params["shading"] = payload["shading"]
    if "camera_view" in payload:
        capture_params["camera_view"] = payload["camera_view"]
    if "format" in payload:
        capture_params["format"] = payload["format"]
    return info_query(
        {"type": "viewport_capture", "params": capture_params}, started=started
    )


def _handle_get_selection(payload: dict[str, Any], started: float) -> dict[str, Any]:
    return info_query({"type": "selection"}, started=started)


# ---------------------------------------------------------------
# Declarative Write Layer
# ---------------------------------------------------------------


def _handle_edit_nodes(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.nodes.editor import node_tree_edit

    return node_tree_edit(payload, started=started)


def _handle_edit_animation(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.animation.editor import animation_edit

    return animation_edit(payload, started=started)


def _handle_edit_sequencer(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.sequencer.editor import sequencer_edit

    return sequencer_edit(payload, started=started)


# ---------------------------------------------------------------
# Imperative Write Layer
# ---------------------------------------------------------------


def _handle_create_object(payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj_name = payload.get("name", "")
    params = {k: v for k, v in payload.items() if k != "name"}
    return data_create(
        {"type": "object", "name": obj_name, "params": params}, started=started
    )


def _handle_modify_object(payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj_name = payload.get("name", "")
    if payload.get("delete"):
        return data_delete(
            {
                "type": "object",
                "name": obj_name,
                "params": {"delete_data": payload.get("delete_data", True)},
            },
            started=started,
        )
    # Handle set_origin via operator
    if "origin" in payload:
        origin_map = {
            "GEOMETRY": "ORIGIN_GEOMETRY",
            "CURSOR": "ORIGIN_CURSOR",
            "MEDIAN": "ORIGIN_CENTER_OF_MASS",
        }
        origin_type = origin_map.get(payload["origin"], payload["origin"])
        operator_execute(
            {
                "operator": "object.origin_set",
                "params": {"type": origin_type},
                "context": {"active_object": obj_name},
            },
            started=started,
        )
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
    return data_write(
        {"type": "object", "name": obj_name, "properties": props}, started=started
    )


def _handle_manage_material(payload: dict[str, Any], started: float) -> dict[str, Any]:
    action = payload.get("action", "")
    name = payload.get("name", "")
    _PBR_KEYS = (
        "base_color",
        "metallic",
        "roughness",
        "specular",
        "alpha",
        "emission_color",
        "emission_strength",
        "use_fake_user",
    )
    if action == "create":
        mat_params = {k: payload[k] for k in _PBR_KEYS if k in payload}
        return data_create(
            {"type": "material", "name": name, "params": mat_params}, started=started
        )
    elif action == "delete":
        return data_delete({"type": "material", "name": name}, started=started)
    elif action in ("assign", "unassign"):
        return data_link(
            {
                "source": {"type": "material", "name": name},
                "target": {"type": "object", "name": payload.get("object_name", "")},
                "unlink": action == "unassign",
                "params": {"slot": payload.get("slot")},
            },
            started=started,
        )
    else:
        # edit action — build properties dict from PBR params
        mat_props = {k: payload[k] for k in _PBR_KEYS if k in payload}
        return data_write(
            {"type": "material", "name": name, "properties": mat_props}, started=started
        )


def _handle_manage_modifier(payload: dict[str, Any], started: float) -> dict[str, Any]:
    action = payload.get("action", "")
    obj = payload.get("object_name", "")
    mod_name = payload.get("modifier_name", "")
    if action == "add":
        return data_create(
            {
                "type": "modifier",
                "name": mod_name,
                "params": {
                    "object": obj,
                    "type": payload.get("modifier_type", ""),
                    "settings": payload.get("settings", {}),
                },
            },
            started=started,
        )
    elif action == "remove":
        return data_delete(
            {"type": "modifier", "name": mod_name, "params": {"object": obj}},
            started=started,
        )
    elif action == "configure":
        return data_write(
            {
                "type": "modifier",
                "name": mod_name,
                "properties": payload.get("settings", {}),
                "params": {"object": obj},
            },
            started=started,
        )
    elif action in ("apply", "move_up", "move_down"):
        op_map = {
            "apply": "object.modifier_apply",
            "move_up": "object.modifier_move_up",
            "move_down": "object.modifier_move_down",
        }
        return operator_execute(
            {
                "operator": op_map[action],
                "params": {"modifier": mod_name},
                "context": {"active_object": obj},
            },
            started=started,
        )
    return _error(
        code="invalid_params",
        message=f"Unknown modifier action: {action}",
        started=started,
    )


def _handle_manage_collection(
    payload: dict[str, Any], started: float
) -> dict[str, Any]:
    action = payload.get("action", "")
    col_name = payload.get("collection_name", "")
    if action == "create":
        col_params: dict[str, Any] = {}
        if "parent" in payload:
            col_params["parent"] = payload["parent"]
        if "color_tag" in payload:
            col_params["color_tag"] = payload["color_tag"]
        return data_create(
            {"type": "collection", "name": col_name, "params": col_params},
            started=started,
        )
    elif action == "delete":
        return data_delete({"type": "collection", "name": col_name}, started=started)
    elif action in ("link_object", "unlink_object"):
        return data_link(
            {
                "source": {"type": "object", "name": payload.get("object_name", "")},
                "target": {"type": "collection", "name": col_name},
                "unlink": action == "unlink_object",
            },
            started=started,
        )
    elif action == "set_visibility":
        vis_props: dict[str, Any] = {}
        if "hide_viewport" in payload:
            vis_props["hide_viewport"] = payload["hide_viewport"]
        if "hide_render" in payload:
            vis_props["hide_render"] = payload["hide_render"]
        return data_write(
            {"type": "collection", "name": col_name, "properties": vis_props},
            started=started,
        )
    elif action == "set_parent":
        return data_link(
            {
                "source": {"type": "collection", "name": col_name},
                "target": {"type": "collection", "name": payload.get("parent", "")},
            },
            started=started,
        )
    return _error(
        code="invalid_params",
        message=f"Unknown collection action: {action}",
        started=started,
    )


def _handle_manage_uv(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.uv.handler import uv_manage

    return uv_manage(payload, started=started)


def _handle_manage_constraints(
    payload: dict[str, Any], started: float
) -> dict[str, Any]:
    from ..handlers.constraints.handler import constraints_manage

    return constraints_manage(payload, started=started)


def _handle_manage_physics(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.physics.handler import physics_manage

    return physics_manage(payload, started=started)


def _handle_setup_scene(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.scene.config import scene_setup

    return scene_setup(payload, started=started)


# ---------------------------------------------------------------
# Fallback Layer
# ---------------------------------------------------------------


def _handle_execute_operator(payload: dict[str, Any], started: float) -> dict[str, Any]:
    return operator_execute(
        {
            "operator": payload.get("operator", ""),
            "params": payload.get("params", {}),
            "context": payload.get("context"),
        },
        started=started,
    )


def _handle_execute_script(payload: dict[str, Any], started: float) -> dict[str, Any]:
    return script_execute(payload, started=started)


def _handle_import_export(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.importexport.handler import import_export

    return import_export(payload, started=started)


# ---------------------------------------------------------------
# Capability dispatch registry
# ---------------------------------------------------------------

_CAPABILITY_HANDLERS: dict[str, Callable[[dict[str, Any], float], dict[str, Any]]] = {
    # Perception Layer
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
    # Declarative Write Layer
    "blender.edit_nodes": _handle_edit_nodes,
    "blender.edit_animation": _handle_edit_animation,
    "blender.edit_sequencer": _handle_edit_sequencer,
    # Imperative Write Layer
    "blender.create_object": _handle_create_object,
    "blender.modify_object": _handle_modify_object,
    "blender.manage_material": _handle_manage_material,
    "blender.manage_modifier": _handle_manage_modifier,
    "blender.manage_collection": _handle_manage_collection,
    "blender.manage_uv": _handle_manage_uv,
    "blender.manage_constraints": _handle_manage_constraints,
    "blender.manage_physics": _handle_manage_physics,
    "blender.setup_scene": _handle_setup_scene,
    # Fallback Layer
    "blender.execute_operator": _handle_execute_operator,
    "blender.execute_script": _handle_execute_script,
    "blender.import_export": _handle_import_export,
}


def _dispatch_new_capability(
    capability: str, payload: dict[str, Any], started: float
) -> dict[str, Any]:
    """Dispatch new blender.* capabilities via registry lookup.

    Maps the 26 new tool internal capabilities to handler calls.
    Many new tools reuse existing handlers with parameter transformations.
    New handlers that require bpy are imported lazily.
    """
    handler = _CAPABILITY_HANDLERS.get(capability)
    if handler is not None:
        return handler(payload, started)
    return _error(
        code="unsupported_capability",
        message=f"new capability '{capability}' not yet implemented",
        data={"capability": capability},
        started=started,
    )


_WRITE_CAPABILITIES = frozenset(
    {
        "blender.edit_nodes",
        "blender.edit_animation",
        "blender.edit_sequencer",
        "blender.create_object",
        "blender.modify_object",
        "blender.manage_material",
        "blender.manage_modifier",
        "blender.manage_collection",
        "blender.manage_uv",
        "blender.manage_constraints",
        "blender.manage_physics",
        "blender.setup_scene",
        "blender.execute_operator",
        "blender.execute_script",
        "blender.import_export",
    }
)


def _push_undo_step(capability: str) -> None:
    """Push an undo step so Ctrl+Z can revert the MCP operation."""
    try:
        import bpy  # type: ignore

        bpy.ops.ed.undo_push(message=f"MCP: {capability}")
    except Exception:
        pass


def execute_capability(request: dict[str, Any]) -> dict[str, Any]:
    """Execute a capability request and return the result.

    Supports internal capabilities (data.*, operator.execute, info.query,
    script.execute) and new blender.* capabilities from the 26-tool architecture.

    Write capabilities are wrapped with an undo-push so that every MCP
    mutation can be reverted with Ctrl+Z in Blender.
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

        if capability.startswith("blender."):
            if capability in _WRITE_CAPABILITIES:
                _push_undo_step(capability)
            return _dispatch_new_capability(capability, payload, started)

        return _error(
            code="unsupported_capability",
            message="capability is not supported by this addon",
            data={"capability": capability},
            started=started,
        )
    except Exception as exc:
        import traceback

        tb = traceback.format_exc()
        try:
            import bpy

            txt = bpy.data.texts.get("__mcp_diag__") or bpy.data.texts.new(
                "__mcp_diag__"
            )
            txt.clear()
            txt.write(f"{type(exc).__name__}: {exc}\n\n{tb}")
        except Exception:
            pass
        return _error(
            code="addon_exception",
            message=f"unhandled: {type(exc).__name__}: {exc}",
            data={"traceback": tb},
            started=started,
        )
