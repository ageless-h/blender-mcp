# -*- coding: utf-8 -*-
"""Blender MCP Addon - MCP server integration for AI-assisted Blender automation.

Notes:
- The addon is normally imported inside Blender where `bpy` is available.
- For unit tests running outside Blender, we avoid importing bpy eagerly to prevent
  import failures. Runtime functions guard on bpy availability.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

try:  # noqa: SIM105 - explicit guard for non-Blender test environments
    import bpy  # type: ignore
except ImportError:  # pragma: no cover - executed only outside Blender
    bpy = None  # type: ignore

if TYPE_CHECKING:
    import bpy  # type: ignore

from .server.socket_server import is_server_running, start_socket_server, stop_socket_server

bl_info = {
    "name": "Blender MCP",
    "author": "Blender MCP Contributors",
    "version": (1, 2, 0),
    "blender": (4, 2, 0),
    "category": "Development",
    "description": "MCP server integration for AI-assisted Blender automation",
}

_logger = logging.getLogger(__name__)


def register() -> None:
    """Register addon components."""
    if bpy is None:  # pragma: no cover - safety for non-Blender environments
        raise ImportError("bpy is not available. register() must be called inside Blender.")
    _logger.info("Registering Blender MCP addon")

    from . import operators, ui
    from .preferences import BlenderMCPPreferences

    bpy.utils.register_class(BlenderMCPPreferences)
    operators.register()
    ui.register()

    prefs = bpy.context.preferences.addons[__name__].preferences
    if prefs.auto_start:
        _logger.info("Auto-starting MCP socket server")
        result = start_socket_server(host=prefs.host, port=prefs.port)
        if result.get("ok"):
            _logger.info(f"Server started on {prefs.host}:{prefs.port}")
        else:
            _logger.warning(f"Failed to auto-start server: {result.get('error')}")

    _logger.info("Blender MCP addon registered")


def unregister() -> None:
    """Unregister addon components."""
    if bpy is None:  # pragma: no cover - safety for non-Blender environments
        raise ImportError("bpy is not available. unregister() must be called inside Blender.")
    _logger.info("Unregistering Blender MCP addon")

    from . import operators, ui
    from .preferences import BlenderMCPPreferences

    if is_server_running():
        _logger.info("Stopping MCP socket server")
        stop_socket_server()

    ui.unregister()
    operators.unregister()
    bpy.utils.unregister_class(BlenderMCPPreferences)

    _logger.info("Blender MCP addon unregistered")
