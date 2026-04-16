# -*- coding: utf-8 -*-
"""Fake bpy.context — simulated Blender context for testing."""

from __future__ import annotations

from typing import Any


class FakeContext:
    def __init__(self) -> None:
        self.scene = None
        self.view_layer = None
        self.selected_objects: list[Any] = []
        self.active_object: Any = None
        self.mode: str = "OBJECT"
        self.area: Any = None
        self.region: Any = None
        self.space_data: Any = None

    class _OverrideManager:
        def __enter__(self, *args, **kwargs):
            return self

        def __exit__(self, *args):
            pass

    def temp_override(self, **kwargs: Any) -> _OverrideManager:
        return self._OverrideManager()
