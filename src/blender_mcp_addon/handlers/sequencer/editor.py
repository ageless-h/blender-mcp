# -*- coding: utf-8 -*-
"""Video Sequence Editor (VSE) handler — add/modify/delete strips, effects, transitions."""

from __future__ import annotations

import logging
from typing import Any

from ..response import _error, _ok, bpy_unavailable_error, check_bpy_available

logger = logging.getLogger(__name__)


def _strips(sed: Any) -> Any:
    return sed.strips if hasattr(sed, "strips") else sed.sequences


def _use_length_param() -> bool:
    try:
        import bpy as _bpy

        return _bpy.app.version >= (5, 0)
    except Exception:
        return False


def _new_effect_kwargs(
    sed: Any, name: str, effect_type: str, channel: int, frame_start: int, frame_end: int, **extra: Any
) -> Any:
    strips = _strips(sed)
    if _use_length_param():
        length = frame_end - frame_start
        return strips.new_effect(
            name=name, type=effect_type, channel=channel, frame_start=frame_start, length=length, **extra
        )
    return strips.new_effect(
        name=name, type=effect_type, channel=channel, frame_start=frame_start, frame_end=frame_end, **extra
    )


def sequencer_edit(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Edit the Video Sequence Editor based on action parameter."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    action = payload.get("action", "")
    if not action:
        return _error(code="invalid_params", message="action is required", started=started)

    try:
        scene = bpy.context.scene
    except (AttributeError, RuntimeError):
        scene = next(iter(bpy.data.scenes), None)
    if scene is None:
        return _error(code="operation_failed", message="No scene available", started=started)
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    sed = scene.sequence_editor

    try:
        if action == "add_strip":
            return _add_strip(bpy, sed, payload, started)
        elif action == "modify_strip":
            return _modify_strip(sed, payload, started)
        elif action == "delete_strip":
            return _delete_strip(sed, payload, started)
        elif action == "add_effect":
            return _add_effect(sed, payload, started)
        elif action == "add_transition":
            return _add_transition(sed, payload, started)
        elif action == "move_strip":
            return _move_strip(sed, payload, started)
        else:
            return _error(
                code="invalid_params",
                message=f"Unknown action: {action}",
                started=started,
            )
    except (AttributeError, KeyError, TypeError, RuntimeError, ValueError) as exc:
        import traceback

        tb = traceback.format_exc()
        logger.error("Sequencer %s failed: %s\n%s", action, exc, tb)
        try:
            import bpy

            txt = bpy.data.texts.get("__mcp_diag__") or bpy.data.texts.new("__mcp_diag__")
            txt.clear()
            txt.write(f"VSE {action}: {type(exc).__name__}: {exc}\n\n{tb}")
        except (AttributeError, RuntimeError):
            pass
        return _error(
            code="operation_failed",
            message=f"{action} failed: {exc}",
            data={"traceback": tb},
            started=started,
        )


def _add_strip(bpy: Any, sed: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    strip_type = payload.get("strip_type", "")
    channel = payload.get("channel", 1)
    frame_start = payload.get("frame_start", 1)

    strip: Any = None
    if strip_type == "COLOR":
        frame_end = payload.get("frame_end", frame_start + 100)
        strip = _new_effect_kwargs(sed, payload.get("strip_name", "Color"), "COLOR", channel, frame_start, frame_end)
        if strip and payload.get("color"):
            strip.color = tuple(payload["color"][:3])
    elif strip_type == "TEXT":
        frame_end = payload.get("frame_end", frame_start + 100)
        strip = _new_effect_kwargs(sed, payload.get("strip_name", "Text"), "TEXT", channel, frame_start, frame_end)
        if strip:
            if payload.get("text"):
                strip.text = payload["text"]
            if payload.get("font_size"):
                strip.font_size = payload["font_size"]
            if payload.get("color"):
                strip.color = tuple(payload["color"][:3])
    elif strip_type == "ADJUSTMENT":
        frame_end = payload.get("frame_end", frame_start + 100)
        strip = _new_effect_kwargs(
            sed, payload.get("strip_name", "Adjustment"), "ADJUSTMENT", channel, frame_start, frame_end
        )
    elif strip_type in ("VIDEO", "IMAGE", "AUDIO"):
        filepath = payload.get("filepath", "")
        if not filepath:
            return _error(
                code="invalid_params",
                message="filepath is required for VIDEO/IMAGE/AUDIO strips",
                started=started,
            )
        if strip_type == "VIDEO":
            strip = _strips(sed).new_movie(
                name=payload.get("strip_name", "Movie"),
                filepath=filepath,
                channel=channel,
                frame_start=frame_start,
            )
        elif strip_type == "IMAGE":
            strip = _strips(sed).new_image(
                name=payload.get("strip_name", "Image"),
                filepath=filepath,
                channel=channel,
                frame_start=frame_start,
            )
        else:
            strip = _strips(sed).new_sound(
                name=payload.get("strip_name", "Sound"),
                filepath=filepath,
                channel=channel,
                frame_start=frame_start,
            )
    else:
        return _error(
            code="invalid_params",
            message=f"Unknown strip_type: {strip_type}",
            started=started,
        )

    if strip is None:
        logger.error(
            "new_effect returned None for strip_type=%s channel=%d frame_start=%d",
            strip_type,
            channel,
            frame_start,
        )
        return _error(
            code="operation_failed",
            message=(
                f"Failed to create {strip_type} strip — Blender returned null (channel {channel}, frame {frame_start})"
            ),
            started=started,
        )

    return _ok(
        result={
            "action": "add_strip",
            "name": strip.name,
            "type": strip_type,
            "channel": strip.channel,
            "frame_start": strip.frame_start,
        },
        started=started,
    )


def _modify_strip(sed: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    strip_name = payload.get("strip_name", "")
    strip = _strips(sed).get(strip_name)
    if not strip:
        return _error(code="not_found", message=f"Strip '{strip_name}' not found", started=started)

    settings = payload.get("settings", {})
    for key, value in settings.items():
        if hasattr(strip, key):
            setattr(strip, key, value)

    return _ok(result={"action": "modify_strip", "name": strip.name}, started=started)


def _delete_strip(sed: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    strip_name = payload.get("strip_name", "")
    strip = _strips(sed).get(strip_name)
    if not strip:
        return _error(code="not_found", message=f"Strip '{strip_name}' not found", started=started)
    _strips(sed).remove(strip)
    return _ok(result={"action": "delete_strip", "removed": strip_name}, started=started)


def _add_effect(sed: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    effect_type = payload.get("effect_type", "")
    strip_name = payload.get("strip_name", "")
    channel = payload.get("channel", 2)
    frame_start = payload.get("frame_start", 1)
    frame_end = payload.get("frame_end", frame_start + 100)

    input_strip = _strips(sed).get(strip_name) if strip_name else None
    extra = {"seq1": input_strip} if input_strip else {}
    strip = _new_effect_kwargs(sed, f"{effect_type}_Effect", effect_type, channel, frame_start, frame_end, **extra)
    if strip is None:
        return _error(
            code="operation_failed",
            message=f"Failed to create {effect_type} effect — Blender returned null",
            started=started,
        )
    return _ok(
        result={"action": "add_effect", "name": strip.name, "type": effect_type},
        started=started,
    )


def _add_transition(sed: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    transition_type = payload.get("transition_type", "CROSS")
    channel = payload.get("channel", 2)
    frame_start = payload.get("frame_start")
    transition_duration = payload.get("transition_duration", 10)

    strip1_name = payload.get("strip1_name", "")
    strip2_name = payload.get("strip2_name", "")

    strip1 = _strips(sed).get(strip1_name) if strip1_name else None
    strip2 = _strips(sed).get(strip2_name) if strip2_name else None

    if not strip1 or not strip2:
        return _error(
            code="invalid_params",
            message="strip1_name and strip2_name are required for transitions",
            started=started,
        )

    if frame_start is None:
        frame_start = int(strip2.frame_start)

    try:
        strip = _new_effect_kwargs(
            sed,
            f"{transition_type}_Transition",
            transition_type,
            channel,
            frame_start,
            frame_start + transition_duration,
            seq1=strip1,
            seq2=strip2,
        )
    except (AttributeError, RuntimeError, TypeError) as exc:
        return _error(
            code="operation_failed",
            message=f"Failed to create {transition_type} transition: {exc}",
            started=started,
        )

    if strip is None:
        return _error(
            code="operation_failed",
            message=f"Blender returned null for {transition_type} transition",
            started=started,
        )

    return _ok(
        result={
            "action": "add_transition",
            "name": strip.name,
            "type": transition_type,
            "channel": strip.channel,
            "frame_start": strip.frame_start,
        },
        started=started,
    )


def _move_strip(sed: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    strip_name = payload.get("strip_name", "")
    strip = _strips(sed).get(strip_name)
    if not strip:
        return _error(code="not_found", message=f"Strip '{strip_name}' not found", started=started)

    if "channel" in payload:
        strip.channel = payload["channel"]
    if "frame_start" in payload:
        strip.frame_start = payload["frame_start"]

    return _ok(
        result={
            "action": "move_strip",
            "name": strip.name,
            "channel": strip.channel,
            "frame_start": strip.frame_start,
        },
        started=started,
    )
