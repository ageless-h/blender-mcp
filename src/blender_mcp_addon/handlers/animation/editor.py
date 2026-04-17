# -*- coding: utf-8 -*-
"""Animation editor — keyframes, NLA strips, drivers, shape keys, timeline."""

from __future__ import annotations

import logging
from typing import Any

from ..response import (
    _error,
    _ok,
    bpy_unavailable_error,
    check_bpy_available,
    operation_failed_error,
)

logger = logging.getLogger(__name__)


def animation_edit(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Edit animation data based on action parameter."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    action = payload.get("action", "")
    if not action:
        return _error(code="invalid_params", message="action is required", started=started)

    try:
        if action == "insert_keyframe":
            return _insert_keyframe(bpy, payload, started)
        elif action == "delete_keyframe":
            return _delete_keyframe(bpy, payload, started)
        elif action == "modify_keyframe":
            return _modify_keyframe(bpy, payload, started)
        elif action == "add_nla_strip":
            return _add_nla_strip(bpy, payload, started)
        elif action == "modify_nla_strip":
            return _modify_nla_strip(bpy, payload, started)
        elif action == "remove_nla_strip":
            return _remove_nla_strip(bpy, payload, started)
        elif action == "add_driver":
            return _add_driver(bpy, payload, started)
        elif action == "remove_driver":
            return _remove_driver(bpy, payload, started)
        elif action == "set_shape_key":
            return _set_shape_key(bpy, payload, started)
        elif action == "set_frame":
            return _set_frame(bpy, payload, started)
        elif action == "set_frame_range":
            return _set_frame_range(bpy, payload, started)
        else:
            return _error(
                code="invalid_params",
                message=f"Unknown action: {action}",
                started=started,
            )
    except (AttributeError, KeyError, TypeError, RuntimeError, ValueError) as exc:
        return operation_failed_error(action, exc, started)


def _get_object(bpy: Any, payload: dict[str, Any], started: float) -> tuple[Any, dict[str, Any] | None]:
    """Get object from payload, returning (obj, error_response_or_None)."""
    name = payload.get("object_name", "")
    if not name:
        return None, _error(code="invalid_params", message="object_name is required", started=started)
    obj = bpy.data.objects.get(name)
    if obj is None:
        return None, _error(code="not_found", message=f"Object '{name}' not found", started=started)
    return obj, None


def _insert_keyframe(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj, err = _get_object(bpy, payload, started)
    if err:
        return err
    data_path = payload.get("data_path", "location")
    index = payload.get("index", -1)
    frame = payload.get("frame", bpy.context.scene.frame_current)
    value = payload.get("value")

    if value is not None:
        prop = obj.path_resolve(data_path)
        if hasattr(prop, "__len__") and index >= 0:
            prop[index] = value
        elif not hasattr(prop, "__len__"):
            setattr(obj, data_path.split(".")[-1], value) if "." not in data_path else None

    obj.keyframe_insert(data_path=data_path, index=index, frame=frame)

    interp = payload.get("interpolation")
    if interp and obj.animation_data and obj.animation_data.action:
        action = obj.animation_data.action
        # Use fcurves.find() for O(1) lookup instead of O(n) iteration
        fc = action.fcurves.find(data_path, index=index if index >= 0 else -1)
        if fc:
            for kp in fc.keyframe_points:
                if int(kp.co[0]) == frame:
                    kp.interpolation = interp
        else:
            logger.warning("FCurve not found for data_path='%s' index=%d", data_path, index)

    return _ok(
        result={
            "action": "insert_keyframe",
            "object": obj.name,
            "data_path": data_path,
            "frame": frame,
        },
        started=started,
    )


def _delete_keyframe(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj, err = _get_object(bpy, payload, started)
    if err:
        return err
    data_path = payload.get("data_path", "location")
    index = payload.get("index", -1)
    frame = payload.get("frame", bpy.context.scene.frame_current)
    obj.keyframe_delete(data_path=data_path, index=index, frame=frame)
    return _ok(
        result={
            "action": "delete_keyframe",
            "object": obj.name,
            "data_path": data_path,
            "frame": frame,
        },
        started=started,
    )


def _modify_keyframe(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj, err = _get_object(bpy, payload, started)
    if err:
        return err
    data_path = payload.get("data_path", "location")
    index = payload.get("index", -1)
    frame = payload.get("frame")
    interp = payload.get("interpolation")
    value = payload.get("value")

    if not obj.animation_data or not obj.animation_data.action:
        return _error(code="not_found", message="No animation data on object", started=started)

    modified = 0
    action = obj.animation_data.action

    # Find the FCurve - use iter_fcurves() for layered actions, fcurves.find() for legacy
    from . import iter_fcurves

    fc = None
    if hasattr(action, "layers"):
        # Blender 5.0+ layered API - iterate to find matching fcurve
        for fcurve in iter_fcurves(action):
            if fcurve.data_path == data_path and (index == -1 or fcurve.array_index == index):
                fc = fcurve
                break
    elif hasattr(action, "fcurves"):
        # Legacy API - use O(1) find() lookup
        fc = action.fcurves.find(data_path, index=index if index >= 0 else -1)

    if fc:
        if value is not None and frame is not None:
            target_frame = int(frame)
            for kp in list(fc.keyframe_points):
                if int(kp.co[0]) == target_frame:
                    new_kp = fc.keyframe_points.insert(float(target_frame), float(value))
                    new_kp.interpolation = interp or kp.interpolation
                    modified += 1
                    break
        elif interp:
            for kp in fc.keyframe_points:
                if frame is None or int(kp.co[0]) == frame:
                    kp.interpolation = interp
                    modified += 1
    else:
        logger.warning("FCurve not found for data_path='%s' index=%d", data_path, index)

    return _ok(
        result={"action": "modify_keyframe", "modified_count": modified},
        started=started,
    )


def _add_nla_strip(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj, err = _get_object(bpy, payload, started)
    if err:
        return err
    action_name = payload.get("nla_action", "")
    nla_action = bpy.data.actions.get(action_name)
    if not nla_action:
        return _error(
            code="not_found",
            message=f"Action '{action_name}' not found",
            started=started,
        )

    if not obj.animation_data:
        obj.animation_data_create()

    track = obj.animation_data.nla_tracks.new()
    start = payload.get("nla_start_frame", 1)
    strip = track.strips.new(nla_action.name, start, nla_action)
    return _ok(
        result={
            "action": "add_nla_strip",
            "strip_name": strip.name,
            "track": track.name,
            "start": start,
        },
        started=started,
    )


def _modify_nla_strip(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj, err = _get_object(bpy, payload, started)
    if err:
        return err
    strip_name = payload.get("nla_strip_name", "")
    if not obj.animation_data:
        return _error(code="not_found", message="No animation data", started=started)

    for track in obj.animation_data.nla_tracks:
        for strip in track.strips:
            if strip.name == strip_name:
                if "nla_start_frame" in payload:
                    strip.frame_start = payload["nla_start_frame"]
                return _ok(
                    result={"action": "modify_nla_strip", "strip": strip.name},
                    started=started,
                )
    return _error(code="not_found", message=f"NLA strip '{strip_name}' not found", started=started)


def _remove_nla_strip(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj, err = _get_object(bpy, payload, started)
    if err:
        return err
    strip_name = payload.get("nla_strip_name", "")
    if not obj.animation_data:
        return _error(code="not_found", message="No animation data", started=started)

    for track in obj.animation_data.nla_tracks:
        for strip in track.strips:
            if strip.name == strip_name:
                track.strips.remove(strip)
                return _ok(
                    result={"action": "remove_nla_strip", "removed": strip_name},
                    started=started,
                )
    return _error(code="not_found", message=f"NLA strip '{strip_name}' not found", started=started)


def _add_driver(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj, err = _get_object(bpy, payload, started)
    if err:
        return err
    data_path = payload.get("data_path", "")
    index = payload.get("index", -1)
    expression = payload.get("driver_expression", "")

    fc = obj.driver_add(data_path, index) if index >= 0 else obj.driver_add(data_path)
    if isinstance(fc, list):
        for f in fc:
            f.driver.expression = expression
    else:
        fc.driver.expression = expression
    return _ok(
        result={
            "action": "add_driver",
            "data_path": data_path,
            "expression": expression,
        },
        started=started,
    )


def _remove_driver(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj, err = _get_object(bpy, payload, started)
    if err:
        return err
    data_path = payload.get("data_path", "")
    index = payload.get("index", -1)
    obj.driver_remove(data_path, index) if index >= 0 else obj.driver_remove(data_path)
    return _ok(result={"action": "remove_driver", "data_path": data_path}, started=started)


def _set_shape_key(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    obj, err = _get_object(bpy, payload, started)
    if err:
        return err
    sk_name = payload.get("shape_key_name", "")
    value = payload.get("value", 0)
    if not obj.data or not obj.data.shape_keys:
        return _error(code="not_found", message="No shape keys on object", started=started)
    kb = obj.data.shape_keys.key_blocks.get(sk_name)
    if not kb:
        return _error(
            code="not_found",
            message=f"Shape key '{sk_name}' not found",
            started=started,
        )
    kb.value = value
    return _ok(
        result={"action": "set_shape_key", "name": sk_name, "value": value},
        started=started,
    )


def _set_frame(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    frame = payload.get("frame_start", payload.get("frame", bpy.context.scene.frame_current))
    bpy.context.scene.frame_set(frame)
    return _ok(result={"action": "set_frame", "frame": frame}, started=started)


def _set_frame_range(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    scene = bpy.context.scene
    if "frame_start" in payload:
        scene.frame_start = payload["frame_start"]
    if "frame_end" in payload:
        scene.frame_end = payload["frame_end"]
    if "fps" in payload:
        scene.render.fps = int(payload["fps"])
    return _ok(
        result={
            "action": "set_frame_range",
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "fps": scene.render.fps,
        },
        started=started,
    )
