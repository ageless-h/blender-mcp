# -*- coding: utf-8 -*-
"""Operators for Blender MCP addon."""
from __future__ import annotations

from typing import TYPE_CHECKING

try:
    import bpy  # type: ignore
except ImportError:  # pragma: no cover - allow imports outside Blender
    bpy = None  # type: ignore

if TYPE_CHECKING:
    import bpy  # type: ignore

from .server.socket_server import (
    is_server_running,
    start_socket_server,
    stop_socket_server,
)

if bpy is not None:
    from bpy.types import Operator  # type: ignore

    class MCP_OT_start_server(Operator):
        """Start the MCP socket server"""

        bl_idname = "mcp.start_server"
        bl_label = "Start MCP Server"
        bl_description = "Start the MCP socket server for AI communication"

        def execute(self, context: bpy.types.Context) -> set[str]:
            if is_server_running():
                self.report({"INFO"}, "Server already running")
                return {"CANCELLED"}

            prefs = context.preferences.addons["blender_mcp_addon"].preferences
            result = start_socket_server(host=prefs.host, port=prefs.port)

            if result.get("ok"):
                self.report({"INFO"}, f"Server started on {prefs.host}:{prefs.port}")
                return {"FINISHED"}
            else:
                self.report({"ERROR"}, f"Failed to start server: {result.get('error')}")
                return {"CANCELLED"}


    class MCP_OT_stop_server(Operator):
        """Stop the MCP socket server"""

        bl_idname = "mcp.stop_server"
        bl_label = "Stop MCP Server"
        bl_description = "Stop the MCP socket server"

        def execute(self, context: bpy.types.Context) -> set[str]:
            if not is_server_running():
                self.report({"INFO"}, "Server not running")
                return {"CANCELLED"}

            result = stop_socket_server()

            if result.get("ok"):
                self.report({"INFO"}, "Server stopped")
                return {"FINISHED"}
            else:
                self.report({"ERROR"}, f"Failed to stop server: {result.get('error')}")
                return {"CANCELLED"}


    classes = (
        MCP_OT_start_server,
        MCP_OT_stop_server,
    )
else:
    classes = ()


def register() -> None:
    """Register operator classes."""
    if bpy is None:  # pragma: no cover - safety for non-Blender environments
        return
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    """Unregister operator classes."""
    if bpy is None:  # pragma: no cover - safety for non-Blender environments
        return
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
