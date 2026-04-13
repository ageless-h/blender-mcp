# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

try:
    import bpy  # type: ignore
    from bpy.props import BoolProperty, IntProperty, StringProperty  # type: ignore
    from bpy.types import Panel, PropertyGroup, UIList  # type: ignore
except ImportError:  # pragma: no cover - allow imports outside Blender
    bpy = None  # type: ignore

if TYPE_CHECKING:
    import bpy  # type: ignore
    from bpy.types import Panel, PropertyGroup, UIList  # type: ignore

from .server.op_log import operation_log
from .server.socket_server import is_server_running

if bpy is not None:
    from bpy.props import CollectionProperty  # type: ignore

    class MCPLogItem(PropertyGroup):
        name: StringProperty()  # type: ignore
        ok: BoolProperty()  # type: ignore
        duration_ms: IntProperty()  # type: ignore
        preview: StringProperty()  # type: ignore

    class BlenderMCPProperties(PropertyGroup):
        show_advanced: BoolProperty(
            name="Show Advanced",
            description="Show advanced connection settings",
            default=False,
        )  # type: ignore

        log_filter: StringProperty(
            name="Filter",
            description="Filter log entries by capability name",
            default="",
        )  # type: ignore

        selected_log_index: IntProperty(default=0)  # type: ignore
        log_entries: CollectionProperty(type=MCPLogItem)  # type: ignore

    class MCP_UL_activity_log(UIList):
        def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
            if not item.name:
                return
            row = layout.row(align=True)
            icon_name = "CHECKMARK" if item.ok else "ERROR"
            row.label(text=item.name, icon=icon_name)
            row.alignment = "RIGHT"
            row.label(text=f"{item.duration_ms:.0f}ms")

    # ── Main panel ──────────────────────────────────────────────────

    class VIEW3D_PT_blender_mcp(Panel):
        bl_label = "Blender MCP"
        bl_idname = "VIEW3D_PT_blender_mcp"
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = "Blender MCP"

        def draw(self, context: bpy.types.Context) -> None:
            layout = self.layout
            prefs = context.preferences.addons["blender_mcp_addon"].preferences
            running = is_server_running()
            props = context.scene.blender_mcp

            # ── Connection Status ──
            status_box = layout.box()
            row = status_box.row()
            if running:
                row.label(text="Status: Running", icon="CHECKMARK")
            else:
                row.label(text="Status: Stopped", icon="X")

            if running:
                status_box.label(text=f"{prefs.host}:{prefs.port}", icon="URL")

            # ── Start / Stop ──
            layout.separator()
            if running:
                layout.operator("mcp.stop_server", text="Stop Server", icon="PAUSE")
            else:
                layout.operator("mcp.start_server", text="Start Server", icon="PLAY")

            # ── Connection Settings ──
            layout.separator()
            layout.prop(props, "show_advanced", text="Connection Settings", icon="PREFERENCES")
            if props.show_advanced:
                settings_box = layout.box()
                settings_box.prop(prefs, "host")
                settings_box.prop(prefs, "port")
                settings_box.prop(prefs, "auto_start")

            # ── Activity Log ──
            layout.separator()
            try:
                stats = operation_log.stats
                header_row = layout.row()
                header_row.label(
                    text=f"Requests: {stats['total']}  Errors: {stats['errors']}",
                    icon="TEXT",
                )
                header_row.operator("mcp.clear_log", text="", icon="TRASH")

                # Populate the temp collection from real log
                log_coll = props.log_entries
                log_coll.clear()
                filter_text = props.log_filter.lower()
                for entry in reversed(operation_log.entries):
                    if filter_text and filter_text not in entry.capability.lower():
                        continue
                    item = log_coll.add()
                    cap_short = entry.capability.replace("blender.", "")
                    item.name = cap_short
                    item.ok = entry.ok
                    item.duration_ms = int(entry.duration_ms)
                    item.preview = entry.preview

                # Filter box
                layout.prop(props, "log_filter", text="", icon="VIEWZOOM")

                # Scrollable list
                layout.template_list(
                    "MCP_UL_activity_log",
                    "",
                    props,
                    "log_entries",
                    props,
                    "selected_log_index",
                    rows=8,
                )

                # Preview of selected entry
                idx = props.selected_log_index
                if 0 <= idx < len(log_coll):
                    selected = log_coll[idx]
                    if selected.preview:
                        preview_box = layout.box()
                        preview_box.scale_y = 0.8
                        lines = selected.preview[:300]
                        preview_box.label(text=lines, icon="TEXT")

            except Exception as exc:
                layout.label(text=f"Log error: {exc}", icon="ERROR")

    classes = (
        MCPLogItem,
        MCP_UL_activity_log,
        BlenderMCPProperties,
        VIEW3D_PT_blender_mcp,
    )
else:
    classes = ()


def register() -> None:
    if bpy is None:  # pragma: no cover
        return
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blender_mcp = bpy.props.PointerProperty(type=BlenderMCPProperties)


def unregister() -> None:
    if bpy is None:  # pragma: no cover
        return
    if hasattr(bpy.types.Scene, "blender_mcp"):
        del bpy.types.Scene.blender_mcp
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
