# -*- coding: utf-8 -*-
"""New curves handler for unified CRUD operations (Blender 5.0+)."""

from __future__ import annotations

from typing import Any

from ..base import BaseHandler
from ..registry import HandlerRegistry
from ..types import DataType

_CURVES_UNAVAILABLE_MSG = "curves_new requires Blender 5.0+ (bpy.data.curves not available)"


def _curves_available() -> bool:
    try:
        import bpy  # type: ignore

        return hasattr(bpy.data, "curves")
    except ImportError:
        return False


@HandlerRegistry.register
class CurvesNewHandler(BaseHandler):
    data_type = DataType.CURVES_NEW

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        if not _curves_available():
            return {"ok": False, "error": {"code": "unsupported_type", "message": _CURVES_UNAVAILABLE_MSG}}
        import bpy  # type: ignore

        curves = bpy.data.curves.new(name=name)
        return {"name": curves.name}

    def read(self, name: str, path: str | None, params: dict[str, Any]) -> dict[str, Any]:
        if not _curves_available():
            return {"ok": False, "error": {"code": "unsupported_type", "message": _CURVES_UNAVAILABLE_MSG}}
        import bpy  # type: ignore

        curves = bpy.data.curves.get(name)
        if curves is None:
            raise KeyError(f"Curves '{name}' not found")

        if path:
            value = self._get_nested_attr(curves, path)
            return {"name": name, "path": path, "value": value}

        return {
            "name": curves.name,
            "resolution_u": curves.resolution_u,
            "resolution_v": curves.resolution_v,
        }

    def write(self, name: str, properties: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        if not _curves_available():
            return {"ok": False, "error": {"code": "unsupported_type", "message": _CURVES_UNAVAILABLE_MSG}}
        import bpy  # type: ignore

        curves = bpy.data.curves.get(name)
        if curves is None:
            raise KeyError(f"Curves '{name}' not found")

        modified = []
        for prop_path, value in properties.items():
            self._set_nested_attr(curves, prop_path, value)
            modified.append(prop_path)
        return {"name": name, "modified": modified}

    def delete(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        if not _curves_available():
            return {"ok": False, "error": {"code": "unsupported_type", "message": _CURVES_UNAVAILABLE_MSG}}
        import bpy  # type: ignore

        curves = bpy.data.curves.get(name)
        if curves is None:
            raise KeyError(f"Curves '{name}' not found")

        bpy.data.curves.remove(curves)
        return {"deleted": name}

    def list_items(self, filter_params: dict[str, Any] | None) -> dict[str, Any]:
        if not _curves_available():
            return {"ok": False, "error": {"code": "unsupported_type", "message": _CURVES_UNAVAILABLE_MSG}}
        import bpy  # type: ignore

        items = [{"name": c.name, "resolution_u": c.resolution_u} for c in bpy.data.curves]
        return {"items": items, "count": len(items)}
