# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

try:
    import bpy  # type: ignore
    from bpy.props import BoolProperty, IntProperty, StringProperty  # type: ignore
    from bpy.types import PropertyGroup, UIList  # type: ignore
except ImportError:  # pragma: no cover - allow imports outside Blender
    bpy = None  # type: ignore

if TYPE_CHECKING:
    import bpy  # type: ignore
    from bpy.types import PropertyGroup, UIList  # type: ignore

from .server.op_log import operation_log
from .server.socket_server import is_server_running

_ZH = {
    "Running": "运行中",
    "Stopped": "已停止",
    "Start Server": "启动服务",
    "Stop Server": "停止服务",
    "Requests": "请求",
    "Errors": "错误",
    "Filter": "筛选",
    "Log error": "日志错误",
    "Offline": "离线",
}

_EN: dict[str, str] = {}


def _t(key: str) -> str:
    if bpy is None:
        return key
    lang = getattr(bpy.context.preferences.view, "language", "en_US")
    if lang.startswith("zh") and key in _ZH:
        return _ZH[key]
    return key


def _t_fmt(key: str, **kwargs: object) -> str:
    return _t(key).format(**kwargs)


if bpy is not None:
    from bpy.props import CollectionProperty  # type: ignore

    class MCPLogItem(PropertyGroup):
        name: StringProperty()  # type: ignore
        ok: BoolProperty()  # type: ignore
        duration_ms: IntProperty()  # type: ignore
        preview: StringProperty()  # type: ignore

    class BlenderMCPProperties(PropertyGroup):
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

    def populate_log_collection(props: bpy.types.PropertyGroup) -> None:
        log_coll = props.log_entries
        log_coll.clear()
        filter_text = props.log_filter.lower()
        for entry in reversed(operation_log.entries):
            if filter_text and filter_text not in entry.capability.lower():
                continue
            item = log_coll.add()
            item.name = entry.capability.replace("blender.", "")
            item.ok = entry.ok
            item.duration_ms = int(entry.duration_ms)
            item.preview = entry.preview

    def draw_statusbar(self, context: bpy.types.Context) -> None:
        layout = self.layout
        if is_server_running():
            stats = operation_log.stats
            layout.operator(
                "mcp.show_panel",
                text=f"  MCP \u25cf {stats['total']} {_t('Requests')}  {stats['errors']} {_t('Errors')}  ",
                icon="CHECKMARK",
                emboss=False,
            )
        else:
            layout.operator(
                "mcp.show_panel",
                text=f"  MCP \u25cb {_t('Offline')}  ",
                icon="X",
                emboss=False,
            )

    def draw_popup(layout, context: bpy.types.Context) -> None:
        prefs = context.preferences.addons["blender_mcp_addon"].preferences
        running = is_server_running()
        props = context.scene.blender_mcp

        status_box = layout.box()
        row = status_box.row()
        if running:
            row.label(text=f"{_t('Running')}  {prefs.host}:{prefs.port}", icon="CHECKMARK")
            status_box.operator("mcp.stop_server", text=_t("Stop Server"), icon="PAUSE")
        else:
            row.label(text=_t("Stopped"), icon="X")
            status_box.operator("mcp.start_server", text=_t("Start Server"), icon="PLAY")

        layout.separator()
        try:
            stats = operation_log.stats
            header_row = layout.row()
            header_row.label(
                text=f"{_t('Requests')}: {stats['total']}  {_t('Errors')}: {stats['errors']}",
                icon="TEXT",
            )
            header_row.operator("mcp.clear_log", text="", icon="TRASH")

            layout.prop(props, "log_filter", text="", icon="VIEWZOOM")

            layout.template_list(
                "MCP_UL_activity_log",
                "",
                props,
                "log_entries",
                props,
                "selected_log_index",
                rows=8,
            )

            idx = props.selected_log_index
            log_coll = props.log_entries
            if 0 <= idx < len(log_coll):
                selected = log_coll[idx]
                if selected.preview:
                    preview_box = layout.box()
                    preview_box.scale_y = 0.8
                    preview_box.label(text=selected.preview[:300], icon="TEXT")

        except Exception as exc:
            layout.label(text=f"{_t('Log error')}: {exc}", icon="ERROR")

    classes = (
        MCPLogItem,
        MCP_UL_activity_log,
        BlenderMCPProperties,
    )
else:
    classes = ()


def register() -> None:
    if bpy is None:  # pragma: no cover
        return
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blender_mcp = bpy.props.PointerProperty(type=BlenderMCPProperties)
    bpy.types.STATUSBAR_HT_header.append(draw_statusbar)


def unregister() -> None:
    if bpy is None:  # pragma: no cover
        return
    try:
        bpy.types.STATUSBAR_HT_header.remove(draw_statusbar)
    except Exception:  # pragma: no cover
        pass
    if hasattr(bpy.types.Scene, "blender_mcp"):
        del bpy.types.Scene.blender_mcp
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
