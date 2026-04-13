# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

try:
    import bpy  # type: ignore
except ImportError:  # pragma: no cover - allow imports outside Blender
    bpy = None  # type: ignore

if TYPE_CHECKING:
    import bpy  # type: ignore

from .server.op_log import operation_log
from .server.socket_server import (
    is_server_running,
    start_socket_server,
    stop_socket_server,
)

if bpy is not None:
    from bpy.types import Operator  # type: ignore

    class MCP_OT_start_server(Operator):
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

    class MCP_OT_clear_log(Operator):
        bl_idname = "mcp.clear_log"
        bl_label = "Clear Log"
        bl_description = "Clear all activity log entries"

        def execute(self, context: bpy.types.Context) -> set[str]:
            operation_log.clear()
            context.scene.blender_mcp.log_entries.clear()
            self.report({"INFO"}, "Log cleared")
            return {"FINISHED"}

    class MCP_OT_show_panel(Operator):
        bl_idname = "mcp.show_panel"
        bl_label = "Blender MCP"
        bl_description = "Show MCP status panel with activity log"

        def invoke(self, context: bpy.types.Context, event):
            from .ui import populate_log_collection

            populate_log_collection(context.scene.blender_mcp)
            return context.window_manager.invoke_props_dialog(self, width=450)

        def draw(self, context: bpy.types.Context):
            from .ui import draw_popup

            draw_popup(self.layout, context)

        def execute(self, context: bpy.types.Context) -> set[str]:
            return {"FINISHED"}

    classes = (
        MCP_OT_start_server,
        MCP_OT_stop_server,
        MCP_OT_clear_log,
        MCP_OT_show_panel,
    )
else:
    classes = ()


addon_keymaps: list = []


def _key_from_prefs() -> tuple:
    if bpy is None:
        return ("M", True, True, False)
    prefs = bpy.context.preferences.addons.get("blender_mcp_addon")
    if prefs is None:
        return ("M", True, True, False)
    p = prefs.preferences
    return (p.hotkey_key, p.hotkey_ctrl, p.hotkey_shift, p.hotkey_alt)


def register() -> None:
    if bpy is None:  # pragma: no cover
        return
    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        key, ctrl, shift, alt = _key_from_prefs()
        km = wm.keyconfigs.addon.keymaps.new(name="Window", space_type="EMPTY")
        kmi = km.keymap_items.new("mcp.show_panel", key, "PRESS", ctrl=ctrl, shift=shift, alt=alt)
        addon_keymaps.append((km, kmi))


def unregister() -> None:
    if bpy is None:  # pragma: no cover
        return
    for km, _kmi in addon_keymaps:
        km.keymap_items.remove(_kmi)
    addon_keymaps.clear()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


def refresh_keymap() -> None:
    for km, _kmi in addon_keymaps:
        km.keymap_items.remove(_kmi)
    addon_keymaps.clear()

    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        key, ctrl, shift, alt = _key_from_prefs()
        km = wm.keyconfigs.addon.keymaps.new(name="Window", space_type="EMPTY")
        kmi = km.keymap_items.new("mcp.show_panel", key, "PRESS", ctrl=ctrl, shift=shift, alt=alt)
        addon_keymaps.append((km, kmi))
