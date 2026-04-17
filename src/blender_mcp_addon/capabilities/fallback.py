# -*- coding: utf-8 -*-
"""Fallback layer handlers — 4 tools for operator/script/import_export/render."""

from __future__ import annotations

from typing import Any

from ..handlers.operator import operator_execute
from ..handlers.script import script_execute


def _handle_execute_operator(payload: dict[str, Any], started: float) -> dict[str, Any]:
    return operator_execute(
        {
            "operator": payload.get("operator", ""),
            "params": payload.get("params", {}),
            "context": payload.get("context"),
        },
        started=started,
    )


def _handle_execute_script(payload: dict[str, Any], started: float) -> dict[str, Any]:
    return script_execute(payload, started=started)


def _handle_import_export(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.importexport.handler import import_export

    return import_export(payload, started=started)


def _handle_render_scene(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.render.handler import render_scene

    return render_scene(payload, started=started)


FALLBACK_HANDLERS = {
    "blender.execute_operator": _handle_execute_operator,
    "blender.execute_script": _handle_execute_script,
    "blender.import_export": _handle_import_export,
    "blender.render_scene": _handle_render_scene,
}
