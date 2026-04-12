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
    # Blender 5.0+ layered API
    if hasattr(action, "layers") and len(action.layers) > 0:
        for layer in action.layers:
            if hasattr(layer, "strips"):
                for strip in layer.strips:
                    if hasattr(strip, "channelbags"):
                        for cbag in strip.channelbags:
                            if hasattr(cbag, "fcurves"):
                                yield from cbag.fcurves
        return
    # Legacy API (Blender 4.x)
    if hasattr(action, "fcurves"):
        yield from action.fcurves
