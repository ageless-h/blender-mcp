# -*- coding: utf-8 -*-
"""Addon preferences for Blender MCP."""
from __future__ import annotations

import bpy  # type: ignore
from bpy.props import BoolProperty, IntProperty, StringProperty  # type: ignore
from bpy.types import AddonPreferences  # type: ignore


class BlenderMCPPreferences(AddonPreferences):
    """Preferences for Blender MCP addon."""

    bl_idname = __package__

    host: StringProperty(
        name="Host",
        description="Host address for the MCP socket server",
        default="127.0.0.1",
    )  # type: ignore

    port: IntProperty(
        name="Port",
        description="Port number for the MCP socket server",
        default=9876,
        min=1024,
        max=65535,
    )  # type: ignore

    auto_start: BoolProperty(
        name="Auto-start Server",
        description="Automatically start the socket server when addon is enabled",
        default=False,
    )  # type: ignore

    def draw(self, context: bpy.types.Context) -> None:
        """Draw the preferences panel."""
        layout = self.layout

        layout.label(text="Server Settings")
        box = layout.box()
        box.prop(self, "host")
        box.prop(self, "port")
        box.prop(self, "auto_start")

        layout.separator()
        layout.label(text="Server Status")
        status_box = layout.box()

        from .server.socket_server import is_server_running

        if is_server_running():
            status_box.label(text=f"Server running on {self.host}:{self.port}", icon="CHECKMARK")
            status_box.operator("mcp.stop_server", text="Stop Server", icon="PAUSE")
        else:
            status_box.label(text="Server stopped", icon="X")
            status_box.operator("mcp.start_server", text="Start Server", icon="PLAY")
