# -*- coding: utf-8 -*-
"""Animation read/edit handlers for keyframes, NLA, drivers, and shape keys."""

from __future__ import annotations

from typing import Any

# Cache Blender version check at module level to avoid repeated hasattr calls
try:
    import bpy  # type: ignore

    _USE_LAYERED_FCURVES = bpy.app.version >= (5, 0)
except ImportError:
    _USE_LAYERED_FCURVES = False


def iter_fcurves(action: Any):
    """Yield F-Curves from an action, supporting both legacy and Blender 5.0+ layered API.

    In Blender 5.0+, the legacy ``action.fcurves`` attribute was removed in favor
    of the layered animation system (``action.layers → strips → channelbags → fcurves``).
    This helper transparently handles both APIs.

    Args:
        action: A bpy.types.Action (or similar) object.
    """
    # Blender 5.0+ layered API
    if _USE_LAYERED_FCURVES:
        for layer in action.layers:
            for strip in layer.strips:
                for cbag in strip.channelbags:
                    yield from cbag.fcurves
        return
    # Legacy API (Blender 4.x)
    yield from action.fcurves
