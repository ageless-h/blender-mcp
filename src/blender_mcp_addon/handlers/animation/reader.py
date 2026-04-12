# -*- coding: utf-8 -*-
"""Animation data reader — keyframes, F-Curves, NLA, drivers, shape keys."""

from __future__ import annotations

import unicodedata
from typing import Any

from ..response import _error, _ok, bpy_unavailable_error, check_bpy_available
from . import iter_fcurves


def _read_keyframes(
    obj: Any, frame_range: list[int] | None = None
) -> list[dict[str, Any]]:
    """Read keyframe data from an object's animation data."""
    keyframes = []
    if not obj.animation_data or not obj.animation_data.action:
        return keyframes
    for fcurve in iter_fcurves(obj.animation_data.action):
        for kp in fcurve.keyframe_points:
            frame = int(kp.co[0])
            if frame_range and (frame < frame_range[0] or frame > frame_range[1]):
                continue
            keyframes.append(
                {
                    "data_path": fcurve.data_path,
                    "index": fcurve.array_index,
                    "frame": frame,
                    "value": kp.co[1],
                    "interpolation": kp.interpolation,
                }
            )
    return keyframes


def _read_fcurves(obj: Any) -> list[dict[str, Any]]:
    """Read F-Curve summary from an object."""
    curves = []
    if not obj.animation_data or not obj.animation_data.action:
        return curves
    for fc in iter_fcurves(obj.animation_data.action):
        curves.append(
            {
                "data_path": fc.data_path,
                "index": fc.array_index,
                "keyframe_count": len(fc.keyframe_points),
                "muted": fc.mute,
                "extrapolation": fc.extrapolation,
            }
        )
    return curves


def _read_nla(obj: Any) -> list[dict[str, Any]]:
    """Read NLA strips from an object."""
    strips = []
    if not obj.animation_data or not obj.animation_data.nla_tracks:
        return strips
    for track in obj.animation_data.nla_tracks:
        for strip in track.strips:
            strips.append(
                {
                    "track": track.name,
                    "name": strip.name,
                    "action": strip.action.name if strip.action else None,
                    "frame_start": strip.frame_start,
                    "frame_end": strip.frame_end,
                    "mute": strip.mute,
                    "influence": strip.influence,
                    "blend_type": strip.blend_type,
                }
            )
    return strips


def _read_drivers(obj: Any) -> list[dict[str, Any]]:
    """Read drivers from an object."""
    drivers = []
    if not obj.animation_data or not obj.animation_data.drivers:
        return drivers
    for fc in obj.animation_data.drivers:
        driver = fc.driver
        drivers.append(
            {
                "data_path": fc.data_path,
                "index": fc.array_index,
                "expression": driver.expression if driver else "",
                "type": driver.type if driver else "",
            }
        )
    return drivers


def _read_shape_keys(obj: Any) -> list[dict[str, Any]]:
    """Read shape keys from an object."""
    keys = []
    if (
        not hasattr(obj, "data")
        or not hasattr(obj.data, "shape_keys")
        or not obj.data.shape_keys
    ):
        return keys
    for kb in obj.data.shape_keys.key_blocks:
        keys.append(
            {
                "name": kb.name,
                "value": kb.value,
                "mute": kb.mute,
                "slider_min": kb.slider_min,
                "slider_max": kb.slider_max,
            }
        )
    return keys


def animation_read(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Read animation data for an object or scene."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    target = payload.get("target", "")
    if not target:
        return _error(
            code="invalid_params", message="target is required", started=started
        )
    target = unicodedata.normalize("NFC", target)

    include = payload.get("include", ["keyframes"])
    frame_range = payload.get("frame_range")

    if target.lower() == "scene":
        obj = bpy.context.scene
    else:
        obj = bpy.data.objects.get(target)

    if obj is None:
        return _error(
            code="not_found", message=f"Object '{target}' not found", started=started
        )

    result: dict[str, Any] = {"target": target}

    if "keyframes" in include:
        result["keyframes"] = _read_keyframes(obj, frame_range)
    if "fcurves" in include:
        result["fcurves"] = _read_fcurves(obj)
    if "nla" in include:
        result["nla_strips"] = _read_nla(obj)
    if "drivers" in include:
        result["drivers"] = _read_drivers(obj)
    if "shape_keys" in include:
        result["shape_keys"] = _read_shape_keys(obj)

    return _ok(result=result, started=started)
