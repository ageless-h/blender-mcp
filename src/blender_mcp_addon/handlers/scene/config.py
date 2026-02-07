# -*- coding: utf-8 -*-
"""Scene configuration handler — render, output, world, timeline settings."""
from __future__ import annotations

import logging
from typing import Any

from ..response import _ok, _error, check_bpy_available, bpy_unavailable_error

logger = logging.getLogger(__name__)


def scene_setup(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Configure scene-level settings."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    scene = bpy.context.scene
    modified = []

    try:
        # Render engine
        if "engine" in payload:
            scene.render.engine = payload["engine"]
            modified.append("engine")

        # Render samples
        if "samples" in payload:
            samples = payload["samples"]
            if scene.render.engine == "CYCLES":
                scene.cycles.samples = samples
            else:
                scene.eevee.taa_render_samples = samples
            modified.append("samples")

        # Resolution
        if "resolution_x" in payload:
            scene.render.resolution_x = payload["resolution_x"]
            modified.append("resolution_x")
        if "resolution_y" in payload:
            scene.render.resolution_y = payload["resolution_y"]
            modified.append("resolution_y")

        # Output format
        if "output_format" in payload:
            scene.render.image_settings.file_format = payload["output_format"]
            modified.append("output_format")
        if "output_path" in payload:
            scene.render.filepath = payload["output_path"]
            modified.append("output_path")

        # Film
        if "film_transparent" in payload:
            scene.render.film_transparent = payload["film_transparent"]
            modified.append("film_transparent")

        # Denoising
        if "denoising" in payload:
            if scene.render.engine == "CYCLES":
                scene.cycles.use_denoising = payload["denoising"]
            modified.append("denoising")
        if "denoiser" in payload and scene.render.engine == "CYCLES":
            scene.cycles.denoiser = payload["denoiser"]
            modified.append("denoiser")

        # World background
        if "background_color" in payload:
            world = scene.world
            if not world:
                world = bpy.data.worlds.new("World")
                scene.world = world
            if not world.use_nodes:
                world.use_nodes = True
            bg_node = world.node_tree.nodes.get("Background")
            if bg_node:
                color = payload["background_color"]
                bg_node.inputs["Color"].default_value = tuple(color[:4])
            modified.append("background_color")

        if "background_strength" in payload:
            world = scene.world
            if world and world.use_nodes:
                bg_node = world.node_tree.nodes.get("Background")
                if bg_node:
                    bg_node.inputs["Strength"].default_value = payload["background_strength"]
            modified.append("background_strength")

        # Timeline / FPS
        if "fps" in payload:
            scene.render.fps = int(payload["fps"])
            modified.append("fps")
        if "frame_start" in payload:
            scene.frame_start = payload["frame_start"]
            modified.append("frame_start")
        if "frame_end" in payload:
            scene.frame_end = payload["frame_end"]
            modified.append("frame_end")
        if "frame_current" in payload:
            scene.frame_set(payload["frame_current"])
            modified.append("frame_current")

        return _ok(result={
            "action": "setup_scene",
            "modified": modified,
            "engine": scene.render.engine,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y],
            "fps": scene.render.fps,
            "frame_range": [scene.frame_start, scene.frame_end],
        }, started=started)

    except Exception as exc:
        return _error(code="operation_failed", message=f"Scene setup failed: {exc}", started=started)
