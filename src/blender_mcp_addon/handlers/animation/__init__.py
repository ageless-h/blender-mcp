# -*- coding: utf-8 -*-
"""Animation read/edit handlers for keyframes, NLA, drivers, and shape keys."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Cache Blender version check at module load to avoid repeated hasattr calls
_USE_LAYERED_API: bool | None = None


def _detect_layered_api() -> bool:
    """Detect if Blender uses layered animation API (5.0+)."""
    global _USE_LAYERED_API
    if _USE_LAYERED_API is not None:
        return _USE_LAYERED_API
    try:
        import bpy  # type: ignore

        _USE_LAYERED_API = bpy.app.version >= (5, 0)
    except Exception:
        logger.debug("bpy not available, defaulting to legacy animation API")
        _USE_LAYERED_API = False
    return _USE_LAYERED_API


def iter_fcurves(action: Any):
    """Yield F-Curves from an action, supporting both legacy and Blender 5.0+ layered API.

    In Blender 5.0+, the legacy ``action.fcurves`` attribute was removed in favor
    of the layered animation system (``action.layers → strips → channelbags → fcurves``).
    This helper transparently handles both APIs.

    Args:
        action: A bpy.types.Action (or similar) object.
    """
    # Use cached version check for Blender 5.0+ layered API
    if _USE_LAYERED_API is None:
        _detect_layered_api()

    if _USE_LAYERED_API and hasattr(action, "layers"):
        for layer in action.layers:
            for strip in layer.strips:
                for cbag in strip.channelbags:
                    yield from cbag.fcurves
        return
    # Legacy API (Blender 4.x)
    yield from action.fcurves
