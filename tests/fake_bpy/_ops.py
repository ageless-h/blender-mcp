# -*- coding: utf-8 -*-
"""Fake bpy.ops — no-op operator namespace for testing."""

from __future__ import annotations


class _FakeOpNamespace:
    def __getattr__(self, name: str) -> "_FakeOpNamespace":
        return _FakeOpNamespace()

    def __call__(self, *args: object, **kwargs: object) -> dict:
        return {"FINISHED": True}


class FakeOps:
    def __init__(self) -> None:
        self.object = _FakeOpNamespace()
        self.mesh = _FakeOpNamespace()
        self.scene = _FakeOpNamespace()
        self.view3d = _FakeOpNamespace()
        self.screen = _FakeOpNamespace()
        self.uv = _FakeOpNamespace()
        self.anim = _FakeOpNamespace()
