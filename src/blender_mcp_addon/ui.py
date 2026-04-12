# -*- coding: utf-8 -*-
"""Sidebar panel UI for Blender MCP addon.

Provides a VIEW3D N-panel with connection status, start/stop controls,
and host/port configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

try:
    import bpy  # type: ignore
    from bpy.props import BoolProperty, IntProperty  # type: ignore
    from bpy.types import Panel, PropertyGroup  # type: ignore
except ImportError:  # pragma: no cover - allow imports outside Blender
    bpy = None  # type: ignore

if TYPE_CHECKING:
    import bpy  # type: ignore
    from bpy.types import Panel, PropertyGroup  # type: ignore

from .server.op_log import operation_log
from .server.socket_server import is_server_running

if bpy is not None:

    class BlenderMCPProperties(PropertyGroup):
        """Runtime properties for the Blender MCP sidebar panel."""

        show_advanced: BoolProperty(
            name="Show Advanced",
            description="Show advanced connection settings",
            default=False,
        )  # type: ignore

        show_log: BoolProperty(
            name="Show Activity Log",
            default=True,
        )  # type: ignore

        log_lines: IntProperty(
            name="Log Lines",
            default=10,
            min=5,
            max=50,
        )  # type: ignore

    class VIEW3D_PT_blender_mcp(Panel):
        """Blender MCP sidebar panel in the 3D Viewport."""

        bl_label = "Blender MCP"
        bl_idname = "VIEW3D_PT_blender_mcp"
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = "Blender MCP"

        def draw(self, context: bpy.types.Context) -> None:
            layout = self.layout
            prefs = context.preferences.addons["blender_mcp_addon"].preferences
            running = is_server_running()

            # --- Connection Status ---
            status_box = layout.box()
            row = status_box.row()
            if running:
                row.label(text="Status: Running", icon="CHECKMARK")
            else:
                row.label(text="Status: Stopped", icon="X")

            if running:
                status_box.label(text=f"{prefs.host}:{prefs.port}", icon="URL")

            # --- Start / Stop ---
            layout.separator()
            if running:
                layout.operator("mcp.stop_server", text="Stop Server", icon="PAUSE")
            else:
                layout.operator("mcp.start_server", text="Start Server", icon="PLAY")

            # --- Advanced Settings ---
            props = context.scene.blender_mcp
            layout.separator()
            layout.prop(props, "show_advanced", text="Connection Settings", icon="PREFERENCES")
            if props.show_advanced:
                settings_box = layout.box()
                settings_box.prop(prefs, "host")
                settings_box.prop(prefs, "port")
                settings_box.prop(prefs, "auto_start")

            # --- Activity Log ---
            layout.separator()
            stats = operation_log.stats
            stats_row = layout.row()
            stats_row.label(
                text=f"Requests: {stats['total']}  Errors: {stats['error']}",
                icon="TEXT",
            )
            layout.prop(props, "show_log", text="Activity Log", icon="CONSOLE")
            if props.show_log and running:
                log_box = layout.box()
                entries = operation_log.recent(count=props.log_lines)
                if not entries:
                    log_box.label(text="No activity yet", icon="INFO")
                else:
                    for entry in reversed(entries):
                        icon = "CHECKMARK" if entry.ok else "ERROR"
                        cap_short = entry.capability.replace("blender.", "")
                        log_box.label(
                            text=f"{cap_short}  {entry.duration_ms:.0f}ms",
                            icon=icon,
                        )

    classes = (
        BlenderMCPProperties,
        VIEW3D_PT_blender_mcp,
    )
else:
    classes = ()


def register() -> None:
    """Register UI classes."""
    if bpy is None:  # pragma: no cover
        return
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blender_mcp = bpy.props.PointerProperty(type=BlenderMCPProperties)


def unregister() -> None:
    """Unregister UI classes."""
    if bpy is None:  # pragma: no cover
        return
    if hasattr(bpy.types.Scene, "blender_mcp"):
        del bpy.types.Scene.blender_mcp
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
