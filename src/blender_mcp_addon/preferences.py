# -*- coding: utf-8 -*-
from __future__ import annotations

import bpy  # type: ignore
from bpy.props import BoolProperty, EnumProperty, IntProperty, StringProperty  # type: ignore
from bpy.types import AddonPreferences  # type: ignore


def _t(key: str) -> str:
    lang = getattr(bpy.context.preferences.view, "language", "en_US")
    _zh = {
        "Server Settings": "服务设置",
        "Server Status": "服务状态",
        "Host": "主机地址",
        "Port": "端口",
        "Auto-start Server": "自动启动服务",
        "Server running on": "服务运行中",
        "Server stopped": "服务已停止",
        "Stop Server": "停止服务",
        "Start Server": "启动服务",
        "Hotkey Settings": "快捷键设置",
        "Panel Hotkey": "面板快捷键",
        "Key": "按键",
        "Ctrl": "Ctrl",
        "Shift": "Shift",
        "Alt": "Alt",
    }
    if lang.startswith("zh") and key in _zh:
        return _zh[key]
    return key


_KEYMAP_ITEMS = [
    ("A", "A", ""),
    ("B", "B", ""),
    ("C", "C", ""),
    ("D", "D", ""),
    ("E", "E", ""),
    ("F", "F", ""),
    ("G", "G", ""),
    ("H", "H", ""),
    ("I", "I", ""),
    ("J", "J", ""),
    ("K", "K", ""),
    ("L", "L", ""),
    ("M", "M", ""),
    ("N", "N", ""),
    ("O", "O", ""),
    ("P", "P", ""),
    ("Q", "Q", ""),
    ("R", "R", ""),
    ("S", "S", ""),
    ("T", "T", ""),
    ("U", "U", ""),
    ("V", "V", ""),
    ("W", "W", ""),
    ("X", "X", ""),
    ("Y", "Y", ""),
    ("Z", "Z", ""),
    ("ONE", "1", ""),
    ("TWO", "2", ""),
    ("THREE", "3", ""),
    ("FOUR", "4", ""),
    ("FIVE", "5", ""),
    ("SPACE", "SPACE", ""),
    ("TAB", "TAB", ""),
    ("RET", "ENTER", ""),
]


def _update_hotkey(self, context: bpy.types.Context) -> None:
    from .operators import refresh_keymap

    refresh_keymap()


class BlenderMCPPreferences(AddonPreferences):
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

    hotkey_key: EnumProperty(  # type: ignore
        name="Key",
        items=_KEYMAP_ITEMS,
        default="M",
        update=_update_hotkey,
    )
    hotkey_ctrl: BoolProperty(name="Ctrl", default=True, update=_update_hotkey)  # type: ignore
    hotkey_shift: BoolProperty(name="Shift", default=True, update=_update_hotkey)  # type: ignore
    hotkey_alt: BoolProperty(name="Alt", default=False, update=_update_hotkey)  # type: ignore

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout

        layout.label(text=_t("Server Settings"))
        box = layout.box()
        box.prop(self, "host")
        box.prop(self, "port")
        box.prop(self, "auto_start")

        layout.separator()
        layout.label(text=_t("Hotkey Settings"))
        hk_box = layout.box()
        hk_box.prop(self, "hotkey_key")
        mod_row = hk_box.row(align=True)
        for prop_name, label_text in [
            ("hotkey_ctrl", "Ctrl"),
            ("hotkey_shift", "Shift"),
            ("hotkey_alt", "Alt"),
        ]:
            sub = mod_row.row(align=True)
            sub.prop(self, prop_name, text="")
            sub.label(text=label_text, translate=False)

        layout.separator()
        layout.label(text=_t("Server Status"))
        status_box = layout.box()

        from .server.socket_server import is_server_running

        if is_server_running():
            status_box.label(text=f"{_t('Server running on')} {self.host}:{self.port}", icon="CHECKMARK")
            status_box.operator("mcp.stop_server", text=_t("Stop Server"), icon="PAUSE")
        else:
            status_box.label(text=_t("Server stopped"), icon="X")
            status_box.operator("mcp.start_server", text=_t("Start Server"), icon="PLAY")
