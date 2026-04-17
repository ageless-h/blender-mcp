# -*- coding: utf-8 -*-
"""Animation read/edit handlers for keyframes, NLA, drivers, and shape keys."""

from __future__ import annotations

from typing import Any


def iter_fcurves(action: Any):
    """Yield F-Curves from an action, supporting both legacy and Blender 5.0+ layered API.

    In Blender 5.0+, the legacy ``action.fcurves`` attribute was removed in favor
    of the layered animation system (``action.layers → strips → channelbags → fcurves``).
    This helper transparently handles both APIs.

    Args:
        action: A bpy.types.Action (or similar) object.
    """
    # Runtime check: Blender 5.0+ layered API
    if hasattr(action, "layers"):
        for layer in action.layers:
            for strip in layer.strips:
                for cbag in strip.channelbags:
                    yield from cbag.fcurves
        return
    # Legacy API (Blender 4.x)
    yield from action.fcurves
