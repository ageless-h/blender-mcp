# -*- coding: utf-8 -*-
"""Shared context override utilities for Blender operator calls."""

from __future__ import annotations

from typing import Any


def get_view3d_override(bpy: Any, obj: Any | None = None) -> dict[str, Any]:
    """Build a context override dict with window, VIEW_3D area, and WINDOW region.

    Args:
        bpy: The bpy module reference.
        obj: Optional active object to include in the override.

    Returns:
        A dict suitable for ``bpy.context.temp_override(**override)``.
        Contains ``window``, ``area``, and ``region`` keys when a VIEW_3D
        area is available.  If *obj* is provided, ``active_object`` and
        ``selected_objects`` are also set.
    """
    override: dict[str, Any] = {}
    if obj is not None:
        override["active_object"] = obj
        override["selected_objects"] = [obj]
    try:
        window = bpy.context.window
        if window:
            override["window"] = window
            for area in window.screen.areas:
                if area.type == "VIEW_3D":
                    override["area"] = area
                    for region in area.regions:
                        if region.type == "WINDOW":
                            override["region"] = region
                            break
                    break
    except (AttributeError, RuntimeError):
        pass
    return override
