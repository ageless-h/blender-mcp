# -*- coding: utf-8 -*-
"""Imperative write layer handlers — 9 tools for object/material/modifier/etc management."""

from __future__ import annotations

from typing import Any

from ..handlers.error_codes import ErrorCode
from ..handlers.operator import operator_execute
from ..handlers.registry import HandlerRegistry
from ..handlers.response import _error, _ok, not_found_error, operation_failed_error
from ..handlers.types import DataType

# Module-level constant for PBR material keys - avoids recreating tuple on every call
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


def _handle_create_object(payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj_name = payload.get("name", "")
    if not obj_name:
        return _error(code=ErrorCode.INVALID_PARAMS, message="'name' parameter is required", started=started)
    params = {k: v for k, v in payload.items() if k != "name"}
    handler = HandlerRegistry.get(DataType.OBJECT)
    if handler is None:
        return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="object handler not available", started=started)
    try:
        return _ok(result=handler.create(obj_name, params), started=started)
    except (AttributeError, KeyError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("create_object", exc, started)


def _handle_modify_object(payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj_name = payload.get("name", "")
    handler = HandlerRegistry.get(DataType.OBJECT)
    if handler is None:
        return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="object handler not available", started=started)
    if payload.get("delete"):
        try:
            result = handler.delete(obj_name, {"delete_data": payload.get("delete_data", True)})
            result["success"] = True
            return _ok(result=result, started=started)
        except KeyError:
            return not_found_error("object", obj_name, started)
        except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
            return operation_failed_error("modify_object", exc, started)
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
    try:
        result = handler.write(obj_name, props, {})
        result["success"] = True
        return _ok(result=result, started=started)
    except KeyError:
        return not_found_error("object", obj_name, started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("modify_object", exc, started)


def _handle_manage_material(payload: dict[str, Any], started: float) -> dict[str, Any]:
    action = payload.get("action", "")
    name = payload.get("name", "")
    handler = HandlerRegistry.get(DataType.MATERIAL)
    if handler is None:
        return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="material handler not available", started=started)
    try:
        if action == "create":
            mat_params = {k: payload[k] for k in _PBR_KEYS if k in payload}
            return _ok(result=handler.create(name, mat_params), started=started)
        elif action == "delete":
            result = handler.delete(name, {})
            result["success"] = True
            return _ok(result=result, started=started)
        elif action == "duplicate":
            import bpy

            src_mat = bpy.data.materials.get(name)
            if src_mat is None:
                return not_found_error("material", name, started)
            new_name = payload.get("new_name", f"{name}.copy")
            new_mat = src_mat.copy()
            new_mat.name = new_name
            bpy.data.materials.link(new_mat)
            return _ok(
                result={"action": "duplicate", "source": name, "name": new_mat.name},
                started=started,
            )
        elif action in ("assign", "unassign"):
            result = handler.link(
                name,
                DataType.OBJECT,
                payload.get("object_name", ""),
                action == "unassign",
                {"slot": payload.get("slot")},
            )
            if "error" in result:
                return _error(code=ErrorCode.LINK_FAILED, message=result["error"], started=started)
            result["success"] = True
            return _ok(result=result, started=started)
        else:
            mat_props = {k: payload[k] for k in _PBR_KEYS if k in payload}
            result = handler.write(name, mat_props, {})
            result["success"] = True
            return _ok(result=result, started=started)
    except KeyError:
        return not_found_error("material", name, started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("manage_material", exc, started)


def _handle_manage_modifier(payload: dict[str, Any], started: float) -> dict[str, Any]:
    action = payload.get("action", "")
    obj = payload.get("object_name", "")
    mod_name = payload.get("modifier_name", "")
    handler = HandlerRegistry.get(DataType.MODIFIER)
    if handler is None:
        return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="modifier handler not available", started=started)
    try:
        if action == "add":
            result = handler.create(
                mod_name,
                {
                    "object": obj,
                    "type": payload.get("modifier_type", ""),
                    "settings": payload.get("settings", {}),
                },
            )
            return _ok(result=result, started=started)
        elif action == "remove":
            result = handler.delete(mod_name, {"object": obj})
            result["success"] = True
            return _ok(result=result, started=started)
        elif action == "configure":
            result = handler.write(mod_name, payload.get("settings", {}), {"object": obj})
            result["success"] = True
            return _ok(result=result, started=started)
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
    except KeyError:
        return not_found_error("modifier", mod_name, started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("manage_modifier", exc, started)
    return _error(
        code=ErrorCode.INVALID_PARAMS,
        message=f"Unknown modifier action: {action}",
        started=started,
    )


def _handle_manage_collection(payload: dict[str, Any], started: float) -> dict[str, Any]:
    action = payload.get("action", "")
    col_name = payload.get("collection_name", "")
    handler = HandlerRegistry.get(DataType.COLLECTION)
    if handler is None:
        return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="collection handler not available", started=started)
    try:
        if action == "create":
            col_params: dict[str, Any] = {}
            if "parent" in payload:
                col_params["parent"] = payload["parent"]
            if "color_tag" in payload:
                col_params["color_tag"] = payload["color_tag"]
            return _ok(result=handler.create(col_name, col_params), started=started)
        elif action == "delete":
            result = handler.delete(col_name, {})
            result["success"] = True
            return _ok(result=result, started=started)
        elif action in ("link_object", "unlink_object"):
            obj_handler = HandlerRegistry.get(DataType.OBJECT)
            if obj_handler is None:
                return _error(code=ErrorCode.UNSUPPORTED_TYPE, message="object handler not available", started=started)
            result = obj_handler.link(
                payload.get("object_name", ""),
                DataType.COLLECTION,
                col_name,
                action == "unlink_object",
                {},
            )
            if "error" in result:
                return _error(code=ErrorCode.LINK_FAILED, message=result["error"], started=started)
            result["success"] = True
            return _ok(result=result, started=started)
        elif action == "set_visibility":
            vis_props: dict[str, Any] = {}
            if "hide_viewport" in payload:
                vis_props["hide_viewport"] = payload["hide_viewport"]
            if "hide_render" in payload:
                vis_props["hide_render"] = payload["hide_render"]
            result = handler.write(col_name, vis_props, {})
            result["success"] = True
            return _ok(result=result, started=started)
        elif action == "set_parent":
            result = handler.link(
                col_name,
                DataType.COLLECTION,
                payload.get("parent", ""),
                False,
                {},
            )
            if "error" in result:
                return _error(code=ErrorCode.LINK_FAILED, message=result["error"], started=started)
            result["success"] = True
            return _ok(result=result, started=started)
    except KeyError:
        return not_found_error("collection", col_name, started)
    except (AttributeError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error("manage_collection", exc, started)
    return _error(
        code=ErrorCode.INVALID_PARAMS,
        message=f"Unknown collection action: {action}",
        started=started,
    )


def _handle_manage_uv(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.uv.handler import uv_manage

    return uv_manage(payload, started=started)


def _handle_manage_constraints(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.constraints.handler import constraints_manage

    return constraints_manage(payload, started=started)


def _handle_manage_physics(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.physics.handler import physics_manage

    return physics_manage(payload, started=started)


def _handle_setup_scene(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.scene.config import scene_setup

    return scene_setup(payload, started=started)


IMPERATIVE_HANDLERS = {
    "blender.create_object": _handle_create_object,
    "blender.modify_object": _handle_modify_object,
    "blender.manage_material": _handle_manage_material,
    "blender.manage_modifier": _handle_manage_modifier,
    "blender.manage_collection": _handle_manage_collection,
    "blender.manage_uv": _handle_manage_uv,
    "blender.manage_constraints": _handle_manage_constraints,
    "blender.manage_physics": _handle_manage_physics,
    "blender.setup_scene": _handle_setup_scene,
}
