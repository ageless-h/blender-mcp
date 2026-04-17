# -*- coding: utf-8 -*-
"""Render handler — render scene to image file."""

from __future__ import annotations

import logging
import os
import tempfile
from typing import Any, Callable

from ..error_codes import ErrorCode
from ..response import _error, _ok, bpy_unavailable_error, check_bpy_available

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[float, float | None, str | None], None] | None


def _get_progress_callback(payload: dict[str, Any]) -> ProgressCallback:
    return payload.pop("_progress_callback", None)


def render_scene(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Render the current scene to an image file.

    Args:
        payload: Render parameters:
            - output_path: Path to save the rendered image (required)
            - resolution_x: Optional X resolution override
            - resolution_y: Optional Y resolution override
            - samples: Optional render samples (Cycles only)
            - animation: If True, render animation frames
            - frame_start: Start frame for animation render
            - frame_end: End frame for animation render
            - use_viewport: If True, use viewport render (EEVEE only)

    Returns:
        Dict with render result info
    """
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    progress = _get_progress_callback(payload)
    output_path = payload.get("output_path", "")

    if not output_path:
        return _error(code=ErrorCode.INVALID_PARAMS, message="output_path is required", started=started)

    scene = bpy.context.scene
    render = scene.render

    original_settings = {
        "resolution_x": render.resolution_x,
        "resolution_y": render.resolution_y,
        "filepath": render.filepath,
    }

    if render.engine == "CYCLES":
        original_settings["samples"] = scene.cycles.samples if hasattr(scene.cycles, "samples") else None

    try:
        if progress:
            progress(0.0, 1.0, "Preparing render settings...")

        if "resolution_x" in payload:
            render.resolution_x = payload["resolution_x"]
        if "resolution_y" in payload:
            render.resolution_y = payload["resolution_y"]

        if render.engine == "CYCLES" and "samples" in payload:
            if hasattr(scene.cycles, "samples"):
                scene.cycles.samples = payload["samples"]

        abs_output_path = os.path.abspath(output_path)
        output_dir = os.path.dirname(abs_output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        render.filepath = abs_output_path

        use_viewport = payload.get("use_viewport", False)
        animation = payload.get("animation", False)

        if animation:
            frame_start = payload.get("frame_start", scene.frame_start)
            frame_end = payload.get("frame_end", scene.frame_end)
            scene.frame_start = frame_start
            scene.frame_end = frame_end

            if progress:
                total_frames = frame_end - frame_start + 1
                progress(0.1, 1.0, f"Rendering animation: {total_frames} frames")

            bpy.ops.render.render(animation=True, write_still=True)

            if progress:
                progress(1.0, 1.0, "Animation render complete")

            return _ok(
                result={
                    "success": True,
                    "output_path": abs_output_path,
                    "animation": True,
                    "frame_start": frame_start,
                    "frame_end": frame_end,
                },
                started=started,
            )
        else:
            if progress:
                progress(0.2, 1.0, "Rendering frame...")

            if use_viewport and render.engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
                bpy.ops.render.opengl(write_still=True)
            else:
                bpy.ops.render.render(write_still=True)

            if progress:
                progress(1.0, 1.0, "Render complete")

            actual_path = abs_output_path
            if not os.path.exists(abs_output_path):
                for image in bpy.data.images:
                    if image.name == "Render Result":
                        tmp = tempfile.mktemp(suffix=".png")
                        image.save_render(tmp)
                        if os.path.exists(tmp):
                            import shutil

                            shutil.move(tmp, abs_output_path)
                        break

            return _ok(
                result={
                    "success": True,
                    "output_path": actual_path,
                    "resolution": [render.resolution_x, render.resolution_y],
                    "engine": render.engine,
                },
                started=started,
            )

    except (AttributeError, RuntimeError, OSError) as exc:
        return _error(code=ErrorCode.OPERATION_FAILED, message=f"Render failed: {exc}", started=started)

    finally:
        render.resolution_x = original_settings["resolution_x"]
        render.resolution_y = original_settings["resolution_y"]
        render.filepath = original_settings["filepath"]
        if render.engine == "CYCLES" and "samples" in original_settings:
            if original_settings["samples"] is not None and hasattr(scene.cycles, "samples"):
                scene.cycles.samples = original_settings["samples"]
